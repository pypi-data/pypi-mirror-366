import torch
import numpy as np
from tqdm.auto import tqdm

import numqi.utils
import numqi.dicke
import numqi.random
import numqi.optimize
import numqi.gellmann
import numqi.manifold

from ._misc import get_density_matrix_boundary, hf_interpolate_dm, _ree_bisection_solve


class PureBosonicExt(torch.nn.Module):
    r'''Approximate the relative entropy of entanglement via Pure Bosonic Extension'''
    def __init__(self, dimA:int, dimB:int, kext:int, distance_kind:str='ree'):
        r'''Initialize the module

        Parameters:
            dimA (int): The dimension of the system A
            dimB (int): The dimension of the system B
            kext (int): extension value for system B
            distance_kind (str): The kind of distance, either 'ree' or 'gellmann'
        '''
        super().__init__()
        distance_kind = distance_kind.lower()
        assert distance_kind in {'ree','gellmann'}
        self.distance_kind = distance_kind
        Bij = numqi.dicke.get_partial_trace_ABk_to_AB_index(kext, dimB)
        num_dicke = numqi.dicke.get_dicke_number(kext, dimB)
        tmp0 = [torch.int64,torch.int64,torch.complex128]
        self.Bij = [[torch.tensor(y0,dtype=y1) for y0,y1 in zip(x,tmp0)] for x in Bij]
        self.manifold = numqi.manifold.Sphere(dimA*num_dicke, dtype=torch.complex128, method='quotient')
        self.dimA = dimA
        self.dimB = dimB

        self.dm_torch = None
        self.dm_target = None
        self.tr_rho_log_rho = None
        self.expect_op_T_vec = None
        self._torch_logm = ('pade',6,8) #set it by user

    def set_dm_target(self, rho:np.ndarray):
        r'''Set the target density matrix

        Parameters:
            rho (np.ndarray): The target density matrix
        '''
        assert (rho.ndim==2) and (rho.shape[0]==rho.shape[1]) #drop support for pure state
        # rho = rho[:,np.newaxis] * rho.conj() #pure
        self.dm_target = torch.tensor(rho, dtype=torch.complex128)
        self.tr_rho_log_rho = -numqi.utils.get_von_neumann_entropy(rho)

    def set_expectation_op(self, op:np.ndarray):
        r'''Set the expectation operator

        Parameters:
            op (np.ndarray): Hermitian expectation operator
        '''
        self.dm_target = None
        self.tr_rho_log_rho = None
        self.expect_op_T_vec = torch.tensor(op.T.reshape(-1), dtype=torch.complex128)

    def forward(self):
        tmp1 = self.manifold().reshape(self.dimA,-1)
        dm_torch = numqi.dicke.partial_trace_ABk_to_AB(tmp1, self.Bij)
        self.dm_torch = dm_torch.detach()
        if self.dm_target is not None:
            if self.distance_kind=='gellmann':
                loss = numqi.gellmann.get_density_matrix_distance2(self.dm_target, dm_torch)
            else:
                loss = numqi.utils.get_relative_entropy(self.dm_target, dm_torch, self.tr_rho_log_rho, self._torch_logm)
        else:
            loss = torch.dot(dm_torch.view(-1), self.expect_op_T_vec).real
        return loss

    def get_boundary(self, dm0:np.ndarray, xtol:float=1e-4, converge_tol:float=1e-10, threshold:float=1e-7,
                    num_repeat:int=1, use_tqdm:bool=True, return_info:bool=False, seed:int|None=None):
        r'''Get the boundary of Pure Bosonic Extension

        Parameters:
            dm0 (np.ndarray): The initial density matrix
            xtol (float): The tolerance for the boundary
            converge_tol (float): The convergence tolerance for optimization
            threshold (float): The threshold for the boundary
            num_repeat (int): The number of repeat for optimization
            use_tqdm (bool): Whether to use tqdm
            return_info (bool): Whether to return the history information
            seed (int|None): The random seed

        Returns:
            beta (float): length of the boundary
            history_info (list): The history information, only if return_info is True
        '''
        beta_u = get_density_matrix_boundary(dm0)[1]
        dm0_norm = numqi.gellmann.dm_to_gellmann_norm(dm0)
        np_rng = numqi.random.get_numpy_rng(seed)
        def hf0(beta):
            # use alpha to avoid time-consuming gellmann conversion
            tmp0 = hf_interpolate_dm(dm0, alpha=beta/dm0_norm)
            self.set_dm_target(tmp0)
            theta_optim = numqi.optimize.minimize(self, theta0='uniform',
                        tol=converge_tol, num_repeat=num_repeat, seed=np_rng, print_every_round=0)
            return float(theta_optim.fun)
        beta,history_info = _ree_bisection_solve(hf0, 0, beta_u, xtol, threshold, use_tqdm=use_tqdm)
        ret = (beta,history_info) if return_info else beta
        return ret

    def get_numerical_range(self, op0:np.ndarray, op1:np.ndarray, num_theta:int=400, converge_tol:float=1e-5,
                            num_repeat:int=1, use_tqdm:bool=True, seed:int|None=None):
        r'''Get the numerical range of Pure Bosonic Extension

        Parameters:
            op0 (np.ndarray): Hermitian expectation operator
            op1 (np.ndarray): Hermitian expectation operator
            num_theta (int): The number of theta
            converge_tol (float): The convergence tolerance for optimization
            num_repeat (int): The number of repeat for optimization
            use_tqdm (bool): Whether to use tqdm
            seed (int|None): The random seed

        Returns:
            ret (np.ndarray): The numerical range, `shape=(num_theta,2)`
        '''
        np_rng = numqi.random.get_numpy_rng(seed)
        N0 = self.dimA*self.dimB
        assert (op0.shape==(N0,N0)) and (op1.shape==(N0,N0))
        theta_list = np.linspace(0, 2*np.pi, num_theta)
        ret = []
        kwargs = dict(num_repeat=num_repeat, seed=np_rng, print_every_round=0, tol=converge_tol)
        for theta_i in (tqdm(theta_list) if use_tqdm else theta_list):
            # see numqi.entangle.get_ppt_numerical_range, we use the maximization there
            self.set_expectation_op(-np.cos(theta_i)*op0 - np.sin(theta_i)*op1)
            numqi.optimize.minimize(self, **kwargs)
            rho = self.dm_torch.detach().numpy()
            ret.append([np.trace(x @ rho).real for x in [op0,op1]])
        ret = np.array(ret)
        return ret

# TODO
# class PureBosonicExtMixed(torch.nn.Module):
#     def __init__(self, dimA, dimB, num_mix) -> None:
#         super().__init__()
#         self.num_mix = num_mix
#         self.dimA = dimA
#         self.dimB = dimB
#         np_rng = np.random.default_rng()
#         tmp0 = np_rng.uniform(num_mix)
#         self.probability = torch.nn.Parameter(torch.tensor(tmp0/tmp0.sum(), dtype=torch.float64))
#         self.pureb_list = torch.nn.ModuleList([numqi.pureb.PureBosonicExt(dimA, dimB) for _ in range(num_mix)])
