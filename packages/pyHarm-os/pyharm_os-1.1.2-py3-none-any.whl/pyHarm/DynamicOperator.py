# Copyright 2024 SAFRAN SA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
from scipy.linalg import block_diag

def get_array_nh(nh:int|list[int]) -> tuple[np.ndarray,bool,int]:
    _is_h0 = False
    if isinstance(nh,int) : 
        anh = np.arange(0, nh+1)
    elif isinstance(nh,list) : 
       anh = np.array(nh).astype(int)
    _h_blocks = 2 * len(anh)
    if 0 in anh : _is_h0 = True; _h_blocks += -1
    return anh, _is_h0, _h_blocks

def get_block_anh(anh:np.ndarray, is_h0:bool, h_block:int) :
    if not is_h0 : 
        banh = np.kron(anh, np.ones(2))
    else : 
        banh = np.concatenate(
            [anh[0:1],np.kron(anh[1:], np.ones(2))],
            axis=0
        )
    return banh

def compute_DFT(nti:int, nh:int|list[int]) -> dict[str:np.ndarray]:
    """
    Builds the Discrete Fourier Transform (DFT) operator adapted to the desired number of time samples and harmonics.
    
    Args:
        nti (int): Number of time steps.
        nh (int): Number of harmonics.
        
    Returns:
        dict[np.ndarray]: Dictionary containing DFT and DTF operators.
    """
    _anh, _is_h0, _ = get_array_nh(nh)
    _len_anh = len(_anh)
    _dft_operator = np.zeros((2*_len_anh, nti))
    _dtf_operator = np.zeros((nti, 2*_len_anh))

    _dft_operator[0::2, :] = np.cos(
            np.reshape(_anh, (-1, 1)) * np.arange(0, nti)*2.*np.pi/nti
        )
    _dft_operator[1::2, :] = np.sin(
            np.reshape(_anh, (-1, 1)) * np.arange(0, nti)*2.*np.pi/nti
        )
    _dtf_operator[:, 0::2] = np.cos(
            np.reshape(np.arange(0, nti), (-1, 1)) * _anh*2.*np.pi/nti
            ) * 2./nti
    _dtf_operator[:, 1::2]= np.sin(
            np.reshape(np.arange(0, nti), (-1, 1)) * _anh*2.*np.pi/nti
            ) * 2./nti

    if _is_h0 : 
        _dft_operator = np.delete(_dft_operator, 1, axis=0)
        _dtf_operator = np.delete(_dtf_operator, 1, axis=1)
        _dtf_operator[:,0] *= 1/2.

    D = dict(
            ft = _dft_operator,
            tf = _dtf_operator
    )
    return D


def nabla(nh:int|list[int]) -> np.ndarray:
    """
    Builds the Derivation operator.
    
    Args:
        nh (int): Number of harmonics.
        
    Returns:
        np.ndarray: Derivation operator in the frequency domain.
    """
    elem_deriv_op = np.array([[0, 1.0], [-1.0, 0]])
    anh,_is_h0,_ = get_array_nh(nh)
    nabla_matrix = block_diag(*[(i * elem_deriv_op) for i in anh])
    if _is_h0 : 
        nabla_matrix = np.delete(
            np.delete(nabla_matrix, 1, axis=0),
            1, axis=1)
    return nabla_matrix