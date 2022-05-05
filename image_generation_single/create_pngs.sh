#!/bin/bash

function func {
    folder_image='../'$folder_base'/images'
    folder_scene='../'$folder_base'/scenes'
    folder_blend='../'$folder_base'/blendfiles'
    blender --background -noaudio --python $path_run -- \
        --folder_image $folder_image'/'$num_objects \
        --folder_scene $folder_scene'/'$num_objects \
        --folder_blend $folder_blend'/'$num_objects \
        --offset $offset \
        --num_images $num_images
}

export PYTHONHASHSEED=0
export CUDA_VISIBLE_DEVICES='0'

path_run='blend_to_pngs.py'
folder_base='output_single'

num_objects='3_6'
offset=0
num_images=52000
func

num_objects='7_10'
offset=0
num_images=1000
func
