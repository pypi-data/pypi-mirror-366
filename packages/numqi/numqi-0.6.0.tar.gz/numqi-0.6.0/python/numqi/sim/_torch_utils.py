import numpy as np
import torch
import itertools

import numqi.sim.state

from ._internal import _ParameterHolder

class _CircuitFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, *args):
        gate_torch = args[:-2]
        q0 = args[-2]
        if isinstance(q0, torch.Tensor):
            q0 = q0.detach().numpy()
        ind_gate_to_info = args[-1]
        name_list = ind_gate_to_info[-1]
        gate_np_dict = {x:y.detach().numpy() for x,y in zip(name_list, gate_torch)}
        for ind0 in range(max(ind_gate_to_info.keys())+1):
            info = ind_gate_to_info[ind0]
            kind = info['kind']
            if 'ind_torch' in info:
                array = gate_np_dict[info['name']][info['ind_torch']]
            else:
                array = info.get('array', None)
            index = info['index']
            gate = info.get('gate', None)
            if kind=='unitary':
                q0 = numqi.sim.state.apply_gate(q0, array, index)
            elif kind=='control':
                q0 = numqi.sim.state.apply_control_n_gate(q0, array, index[0], index[1])
            elif kind=='measure':
                q0 = gate.forward(q0)
            elif kind=='custom':
                q0 = gate.forward(q0)
            else:
                assert False, f'{gate} not supported'
        q0_torch = torch.from_numpy(q0)
        ctx.save_for_backward(q0_torch)
        ctx._numqi_data = dict(ind_gate_to_info=ind_gate_to_info, gate_np_dict=gate_np_dict)
        return q0_torch

    @staticmethod
    @torch.autograd.function.once_differentiable
    def backward(ctx, grad_output):
        tmp0 = ctx._numqi_data
        ind_gate_to_info = tmp0['ind_gate_to_info']
        gate_np_dict = tmp0['gate_np_dict']
        gate_grad_np_dict = {k:np.zeros_like(v) for k,v in gate_np_dict.items()}
        q0_conj = ctx.saved_tensors[0].detach().numpy().conj()
        q0_grad = grad_output.detach().numpy()
        for ind0 in reversed(range(max(ind_gate_to_info.keys())+1)):
            info = ind_gate_to_info[ind0]
            kind = info['kind']
            name = info['name']
            assert kind!='measure', 'not support measure in gradient backward yet'
            require_grad = 'ind_torch' in info
            if require_grad:
                array = gate_np_dict[info['name']][info['ind_torch']]
            else:
                array = info.get('array', None)
            index = info['index']
            gate = info.get('gate', None)
            if kind=='control':
                q0_conj, q0_grad, op_grad = numqi.sim.state.apply_control_n_gate_grad(
                        q0_conj, q0_grad, array, index[0], index[1], tag_op_grad=require_grad)
            elif kind=='unitary':
                q0_conj, q0_grad, op_grad = numqi.sim.state.apply_gate_grad(q0_conj,
                        q0_grad, array, index, tag_op_grad=require_grad)
            elif kind=='custom':
                q0_conj, q0_grad, op_grad = gate.grad_backward(q0_conj, q0_grad)#TODO
            else:
                raise KeyError(f'not recognized gate "{gate}"')
            if require_grad:
                gate_grad_np_dict[name][info['ind_torch']] += op_grad
        name_list = ind_gate_to_info[-1]
        ret = tuple(torch.from_numpy(gate_grad_np_dict[x]) for x in name_list) + (torch.from_numpy(q0_grad),None)
        return ret


def _get_first_come_id(object_list, index_list):
    id_to_index = dict()
    ret = []
    for ind0,object in enumerate(object_list):
        id_ = id(object)
        if id_ not in id_to_index:
            id_to_index[id_] = len(id_to_index)
            ret.append([index_list[ind0]])
        else:
            ret[id_to_index[id_]].append(index_list[ind0])
    return ret


class CircuitTorchWrapper(torch.nn.Module):
    def __init__(self, circuit):
        super().__init__()
        self.circuit = circuit
        self.num_qubit = circuit.num_qubit
        self._setup(circuit.gate_index_list)

    def _setup(self, gate_index_list):
        hf0 = lambda x: x.name
        tmp0 = (x for x,_ in gate_index_list)
        tmp0 = {x:list(y) for x,y in itertools.groupby(sorted(tmp0, key=hf0), key=hf0)}
        # for each name, all hf0 must be the same
        hf0_dict = dict()
        for key,value in tmp0.items():
            assert len({x.kind for x in value})==1
            tmp1 = [x.hf0 for x in value if hasattr(x, 'hf0')]
            if len(tmp1)>1:
                assert all(x==tmp1[0] for x in tmp1[1:])
            if any((x.requires_grad or (hasattr(x,'args') and isinstance(x.args, _ParameterHolder))) for x in value):
                hf0_dict[key] = value[0].hf0

        # pgate
        theta = dict()
        ind_theta_to_ind_gate = dict()
        tmp0 = [(ind0,x) for ind0,(x,_) in enumerate(gate_index_list) if (x.requires_grad) and (not isinstance(x.args, _ParameterHolder))]
        hf0 = lambda x: x[1].name
        tmp0 = {x:list(y) for x,y in itertools.groupby(sorted(tmp0, key=hf0), key=hf0)}
        for key,value in tmp0.items():
            tmp1 = _get_first_come_id([x[1] for x in value], [x[0] for x in value])
            tmp2 = torch.from_numpy(np.array([gate_index_list[x[0]][0].args for x in tmp1], dtype=np.float64))
            theta[key] = torch.nn.Parameter(tmp2)
            ind_theta_to_ind_gate[key] = tmp1
        ind_gate_to_ind_theta = {y:(k,x0) for k,v in ind_theta_to_ind_gate.items() for x0,x1 in enumerate(v) for y in x1}

        # hgate_name_list
        hgate_list = [x for x,_ in gate_index_list if (hasattr(x,'args') and isinstance(x.args, _ParameterHolder))]
        assert len(hgate_list)==len(set(id(x) for x in hgate_list)), 'PlaceHolder gate cannot be re-used'
        tmp0 = [(ind0,x) for ind0,(x,_) in enumerate(gate_index_list) if (hasattr(x,'args') and isinstance(x.args, _ParameterHolder))]
        hf0 = lambda x: x[1].name
        ind_torch_to_ind_hgate = {x:[z[0] for z in y] for x,y in itertools.groupby(sorted(tmp0, key=hf0), key=hf0)}
        tmp0 = {x1:(k,(x0+len(ind_theta_to_ind_gate.get(k,[])))) for k,v in ind_torch_to_ind_hgate.items() for x0,x1 in enumerate(v)}
        assert len(set(tmp0.keys()).intersection(set(ind_gate_to_ind_theta.keys())))==0
        ind_gate_to_ind_torch = ind_gate_to_ind_theta | tmp0

        hpgate_name_list = sorted({x[0] for x in ind_gate_to_ind_torch.values()})
        ind_gate_to_info = {-1: hpgate_name_list}
        for ind0,(gate,index) in enumerate(gate_index_list):
            kind = gate.kind
            name = gate.name
            if ind0 in ind_gate_to_ind_torch:
                ind_torch = ind_gate_to_ind_torch[ind0][1]
                if kind=='custom':
                    info = dict(kind=kind, name=name, index=index, gate=gate)
                else:
                    assert kind in {'unitary','control'}
                    info = dict(kind=kind, name=name, index=index, ind_torch=ind_torch)
            else:
                if kind in {'unitary','control'}:
                    info = dict(kind=kind, name=name, index=index, array=gate.array)
                else: #custom measure
                    info = dict(kind=kind, name=name, index=index, gate=gate)
            ind_gate_to_info[ind0] = info

        self.ind_theta_to_ind_gate = ind_theta_to_ind_gate
        # ind_theta_to_ind_gate: (dict, str, (list, (list,int)))
        self.ind_gate_to_ind_theta = ind_gate_to_ind_theta
        # ind_gate_to_ind_theta: (dict, int, (str, int))
        self.theta = torch.nn.ParameterDict(theta)
        # theta(torch.nn.ParameterDict)
        self.hf0_dict = hf0_dict
        # hf0_dict(dict, str, function)
        self.ind_gate_to_info = ind_gate_to_info
        # key=-1: (list,str) list of pgate name
        # key=0...: dict
        #   kind: str, control, unitary, measure, custom
        #   name: str
        #   index: (tuple,int)
        #   ind_torch: int, required for pgate
        #   array: np.ndarray, required for kind=unitary or kind=control
        #   gate: Gate, required for kind=custom

        self.ind_gate_to_ind_torch = ind_gate_to_ind_torch
        self.ind_torch_to_ind_hgate = ind_torch_to_ind_hgate
        self.hgate_torch_dict = {}

    def setP(self, *args, **kwargs):
        if len(args)>0:
            assert len(args)==1
            self.circuit._P[''] = args[0]
        for k,v in kwargs.items():
            self.circuit._P[k] = v
        self.hgate_torch_dict.clear()
        for key,value in self.ind_torch_to_ind_hgate.items():
            tmp0 = [self.circuit.gate_index_list[x][0].args.resolve() for x in value]
            tmp1 = torch.stack(tmp0).reshape(len(tmp0), -1)
            self.hgate_torch_dict[key] = self.hf0_dict[key](*tmp1.T)

    def forward(self, q0):
        pgate_torch_dict = {k: self.hf0_dict[k](*v.T) for k,v in self.theta.items()}
        # custom pgate must be set_args before calling
        tmp0 = [x for x in self.theta.keys() if (self.circuit.gate_index_list[self.ind_theta_to_ind_gate[x][0][0]][0].kind=='custom')]
        for name in tmp0:
            tmp0 = pgate_torch_dict[name].detach().numpy()
            tmp1 = self.theta[name].detach().numpy()
            for x0,x1 in enumerate(self.ind_theta_to_ind_gate[name]):
                self.circuit.gate_index_list[x1[0]][0].set_args(tmp1[x0], tmp0[x0])
        tmp0 = sorted({x[0] for x in self.ind_gate_to_ind_torch.values()})
        gate_torch_list = []
        for key in tmp0:
            x = pgate_torch_dict.get(key, None)
            y = self.hgate_torch_dict.get(key, None)
            assert not ((x is None) and (y is None))
            if x is None:
                gate_torch_list.append(y)
            elif y is None:
                gate_torch_list.append(x)
            else:
                gate_torch_list.append(torch.concat([x,y], axis=0))
        q0 = _CircuitFunction.apply(*gate_torch_list, q0, self.ind_gate_to_info)
        return q0

    def fresh_gate_parameter(self):
        with torch.no_grad():
            gate_torch_dict = {k: self.hf0_dict[k](*v.T) for k,v in self.theta.items()}
        for name in gate_torch_dict.keys():
            tmp0 = gate_torch_dict[name].detach().numpy()
            tmp1 = self.theta[name].detach().numpy()
            for x0,x1 in enumerate(self.ind_theta_to_ind_gate[name]):
                self.circuit.gate_index_list[x1[0]][0].set_args(tmp1[x0], tmp0[x0])
