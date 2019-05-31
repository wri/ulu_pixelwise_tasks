from numba.pycc import CC
import numpy as np

cc = CC('window_cloud_scores')
cc.verbose = True
cc.output_dir='/cache'
cc.output_file='window_cloud_scores.so'


@cc.export('run', 'f8[:,:](u1[:,:], i4)')
def run(clouds,window):
    r=int(window/2)
    assert clouds.ndim==2
    assert clouds.shape[0]==clouds.shape[1]
    rows,cols=clouds.shape
    score_map=np.full(clouds.shape,-1)
    scores=[]
    for j in range(r,rows-r):
        score_cols=[]
        for i in range(r,cols-r):
            clouds_window=clouds[j-r:j+r+1,i-r:i+r+1]
            score_cols.append(clouds_window.mean())
        scores.append(score_cols)
    return np.array(scores)


if __name__ == "__main__":
    cc.compile()