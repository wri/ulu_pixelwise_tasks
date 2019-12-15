from __future__ import print_function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
""" UrbanLandUse: image_sample_generator.py
- minimal edits
"""
import numpy as np
from tensorflow.python.keras.utils import Sequence
import utils.helpers as h
from config import WINDOW_PADDING
#
# Helpers
#
def preprocess(im,bands_last=False,pop_alpha=True):
    """
    - drop alpha
    - rescale
    - clip: 0,1
    """
    if pop_alpha:
        if bands_last:
            im=im[:,:,:-1]
        else:
            im=im[:-1]
    return (im/10000.0).clip(0.0,1.0)


#
# ImageSampleGenerator
#
class ImageSampleGenerator(Sequence):
    
    # constructor stuff
    def __init__(self,
                image,
                pad=WINDOW_PADDING,
                look_window=17,
                prep_image=False,
                bands_first_model=False):
        self.bands_last=True
        self.bands_first_model=bands_first_model
        if prep_image:
            image=preprocess(image,self.bands_last)
        self.image=image
        self.pad=h.get_padding(pad,look_window)
        self.look_window=look_window
        self._set_data(image)
    
    # eventually this should all be happening beforehand
    # want to just pass the prepared, fused input_stack to generator constructor
    def _prep_image(self,image):
      return 


    def _set_data(self,image):
        assert isinstance(image,np.ndarray)
        # can relax conditions later
        assert image.ndim==3
        if self.bands_last:
            assert image.shape[0]==image.shape[1]
        else:
            assert image.shape[1]==image.shape[2]
        self.batch_size=(image.shape[1]-self.pad-self.pad)
        self.size=self.batch_size^2
        # for starters, will make columns into batches/steps
        self.steps=self.batch_size
        self.reset()


    def __len__(self):
        'Denotes the number of batches per epoch'
        # this may need to be increased by one
        return self.steps


    def reset(self):
        self.batch_index=-1


    def __getitem__(self, index):
        'Generate one batch of data'
        if index >= self.steps or index < 0:
            raise ValueError('illegal batch index:',str(index))
        self.batch_index=index
        inputs=self._get_inputs(index)
        if self.bands_first_model:
            inputs=inputs.swapaxes(3,2).swapaxes(2,1)
        return inputs


    def _get_inputs(self, index):
        look_radius=self.look_window/2
        samples=[]
        for j in range(self.pad,self.image.shape[1]-self.pad):
            sample=h.window(
                self.image,
                j,index+self.pad,
                look_radius,
                bands_first=(not self.bands_last))
            samples.append(sample)
        return np.array(samples)

    