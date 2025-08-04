# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 09:11:54 2024

@author: mgar5380
"""

import os
import glob
import subprocess
from pathlib import Path
import sys
from shutil import rmtree
from platform import system
import SimpleITK as sitk

from platipy.imaging.tests.data import get_lung_nifti, get_lung_dicom
from platipy.imaging.projects.cardiac.run import run_hybrid_segmentation

'''
For testing/ example purposes it's safest to manually append the path variable to ensure our 
package will always be found. This isn't necessary once we actually install the package 
because installation in python essentially means "copying the package to a place where it can be found"
'''
this_file_loc = Path(__file__)
sys.path.insert(0, str(this_file_loc.parent.parent))
# note: insert(0) means that the path is above is the FIRST place that python will look for imports
# sys.path.append means that the path above is the LAST place
from CBCTCardiacSegmentation.CreateCBCTSegmentations import CreateCBCTSegmentations
from CBCTCardiacSegmentation.SegUtil import DoDicomProcessing 
from CBCTCardiacSegmentation.DicomHelper import WriteDicomStructs

def test_DicomProcessing():
    # Download the test data
    data_path = get_lung_dicom()
    test_pat_path = data_path.joinpath("LCTSC-Test-S1-101")
    
    CTDicomDir = test_pat_path.joinpath('1.3.6.1.4.1.14519.5.2.1.7014.4598.106943890850011666503487579262')
    OutputDir='./DicomProcessing'
    DoDicomProcessing(CTDicomDir,OutputDir=OutputDir)
    
    rmtree(data_path)
    rmtree(OutputDir)
    

def test_PlatipyCTSegmentation():
    # Download the test data
    data_path = get_lung_nifti()

    # Pick out a case to run on
    test_pat_path = data_path.joinpath("LCTSC-Test-S1-201")
    test_image = sitk.ReadImage(str(test_pat_path.joinpath("IMAGES/LCTSC_TEST_S1_201_0_CT_0.nii.gz")))

    # Compute the auto-segmented sub-structures
    auto_structures, _ = run_hybrid_segmentation(test_image)

    # Save the results
    output_directory = test_pat_path.joinpath("substructures")
    output_directory.mkdir(exist_ok=True)

    for struct_name in list(auto_structures.keys()):
        sitk.WriteImage(auto_structures[struct_name], str(output_directory.joinpath(f"{struct_name}.nii.gz")))

    print(f"Segmentations saved to: {output_directory}")

    CardiacSegList = ['Heart','A_Aorta','A_Cflx','A_Coronary_L','A_Coronary_R','A_LAD','A_Pulmonary','Atrium_L',
                      'Atrium_R','CN_Atrioventricular','CN_Sinoatrial','V_Venacava_S','Valve_Aortic','Valve_Mitral',
                      'Valve_Pulmonic','Valve_Tricuspid','Ventricle_L','Ventricle_R']
    
    for CardiacSeg in CardiacSegList:
        FileName = os.path.join(output_directory,f"{CardiacSeg}.nii.gz")
        assert Path(FileName).exists(),'File {} does not exist'.format(FileName)    

    rmtree(data_path)

def test_ElastixInstalled():
    
    home_dir = Path(os.path.expanduser('~'))  # may have to update for github system
    elastix_dir = home_dir / 'ElastixDownload' / 'elastix-5.0.1-linux' / 'bin'
    elastix_lib_dir = home_dir / 'ElastixDownload' / 'elastix-5.0.1-linux' / 'lib'
    my_env = os.environ.copy()
    my_env["PATH"] = my_env["PATH"] + ':' + str(elastix_dir)
    if not system() == 'Windows':
        my_env["LD_LIBRARY_PATH"] = my_env["LD_LIBRARY_PATH"] + ':' + str(elastix_lib_dir)
    #bashCommand = "/home/runner/ElastixDownload/elastix-5.0.1-linux/bin/elastix -h"
    bashCommand = "elastix -h"
    subprocess.Popen(bashCommand.split(), env=my_env)
    
def test_BadSegMethodInput():
    # Download the test data
    data_path = get_lung_nifti()

    # Pick out a case to run on
    test_pat_path = data_path.joinpath("LCTSC-Test-S1-201")
    
    SegmentationMethod = ['Test']
    
    CBCTDir = str(test_pat_path.joinpath("IMAGES/LCTSC_TEST_S1_101_0_CT_0.nii.gz"))   #Is a nifti file
    PlanningCTDir = str(test_pat_path.joinpath("IMAGES/LCTSC_TEST_S1_201_0_CT_0.nii.gz"))
    ElastixParamDir = ''
    StructFile = ''
    
    OutputDir = './CBCTSegmentations'    
        
    try:
        CreateCBCTSegmentations(CBCTDir,OutputDir=OutputDir,
                                SegmentationMethod=SegmentationMethod,
                                PlanningCTDir=PlanningCTDir,
                                ElastixParamDir=ElastixParamDir,
                                StructFile=StructFile)
        assert False
    except:
        print('Failed Successfully')
    
    rmtree(data_path) 
    rmtree(OutputDir) 

def test_NiftiCBCTSegmentationGeneration():
    
    # Download the test data
    data_path = get_lung_nifti()

    # Pick out a case to run on
    test_pat_path = data_path.joinpath("LCTSC-Test-S1-201")
    test_pat_path2 = data_path.joinpath("LCTSC-Test-S1-101")
    
    SegmentationMethods = ['Direct','Synthetic','Transform']#,'Test']
    #SegmentationMethods = ['Synthetic','Transform','Direct']#,'Test']
    
    #Use CT images to test functionality until we can get open source CBCT images
    CBCTDir = str(test_pat_path2.joinpath("IMAGES/LCTSC_TEST_S1_101_0_CT_0.nii.gz"))   #Is a nifti file
    PlanningCTDir = str(test_pat_path.joinpath("IMAGES/LCTSC_TEST_S1_201_0_CT_0.nii.gz"))
    ElastixParamDir = ''
    StructFile = ''
    
    #Define Elastix directories
    home_dir = Path(os.path.expanduser('~'))  # may have to update for github system
    elastix_dir = home_dir / 'elastix' / 'elastix-5.0.1-linux'
    
    assert Path(elastix_dir).exists(),'Elastix directory {} does not exist'.format(elastix_dir)
    
    print(glob.glob(os.path.join(elastix_dir,'*')))
    
    for SegMethod in SegmentationMethods:
        print(SegMethod)
        OutputDir = './CBCTSegmentations'    
    
        CreateCBCTSegmentations(CBCTDir,OutputDir=OutputDir,
                                SegmentationMethod=SegMethod,
                                PlanningCTDir=PlanningCTDir,
                                ElastixParamDir=ElastixParamDir,
                                StructFile=StructFile,
                                ElastixRunDir=elastix_dir)
    
        CardiacSegList = ['Heart','A_Aorta','A_Cflx','A_Coronary_L','A_Coronary_R','A_LAD','A_Pulmonary','Atrium_L',
                          'Atrium_R','CN_Atrioventricular','CN_Sinoatrial','V_Venacava_S','Valve_Aortic','Valve_Mitral',
                          'Valve_Pulmonic','Valve_Tricuspid','Ventricle_L','Ventricle_R']
        
        for CardiacSeg in CardiacSegList:
            FileName = os.path.join(OutputDir,'OutputSegmentations_Nifti',f"{CardiacSeg}.nii.gz")
            assert Path(FileName).exists(),'File {} does not exist'.format(FileName)  
    
        #StructFile = os.path.join(OutputDir,'OutputSegmentations_Dicom','struct.dcm')
        #assert Path(StructFile).exists(),'Dicom Struct File {} does not exist'.format(StructFile)
    
        rmtree(OutputDir)    
    rmtree(data_path) 

"""    
Delay testing until we can find some dicom data to test with
def test_DicomCBCTSegmentationGeneration():
    
    # Download the test data
    data_path = get_lung_dicom()
    test_pat_path = data_path.joinpath("LCTSC-Test-S1-101")
    
    CBCTDir = test_pat_path.joinpath('1.3.6.1.4.1.14519.5.2.1.7014.4598.106943890850011666503487579262')
    PlanningCTDir = test_pat_path.joinpath('1.3.6.1.4.1.14519.5.2.1.7014.4598.106943890850011666503487579262')
    
    SegmentationMethods = ['Direct','Synthetic','Transform']#,'Test']
    
    #CBCTDir = '' #Is a dicom directory file
    #PlanningCTDir = ''
    ElastixParamDir = ''
    StructFile = ''
    
    for SegMethod in SegmentationMethods:
        print(SegMethod)
        OutputDir = './CBCTSegmentations'    
    
        CreateCBCTSegmentations(CBCTDir,OutputDir=OutputDir,
                                SegmentationMethod=SegMethod,
                                PlanningCTDir=PlanningCTDir,
                                ElastixParamDir=ElastixParamDir,
                                StructFile=StructFile)
    
        
    
        rmtree(OutputDir)    
        
"""

def test_NiftiToDicomStruct():
    
    data_path = get_lung_dicom()
    test_pat_path = data_path.joinpath("LCTSC-Test-S1-101")
    
    CTDicom = test_pat_path.joinpath('1.3.6.1.4.1.14519.5.2.1.7014.4598.106943890850011666503487579262')    
    StructDicom = test_pat_path.joinpath('1.3.6.1.4.1.14519.5.2.1.7014.4598.280355341349691222365783556597/1-102.dcm')    
    
    OutputDir = './CBCTSegmentations'  
    
    DoDicomProcessing(CTDicom,OutputDir=OutputDir,StructFile = StructDicom)
    
    NiftiStructDir = os.path.join(OutputDir,'Nifti','LCTSC_TEST_S1_101','STRUCTURES')
    
    WriteDicomStructs(NiftiStructDir, CTDicom, OutputDir, CTPat='*dcm')
    
    OutputStructFile = os.path.join(OutputDir,'struct.dcm')
    
    assert Path(OutputStructFile).exists(),'Output Struct {} was not created successfully'.format(OutputStructFile)
    
    rmtree(data_path) 
    rmtree(OutputDir)
