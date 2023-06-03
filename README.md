# NeuroScienceProject
  Preprocessing algorithm for TEP experiment EEG data.
  This code flow locates the TMS pulses contaminated data, removes them and replaces them by cubic interpolation.
  Full description of the project's goals in 'Research problem.docx'.

# To run locally
  Open cmdline in your folder and run : pip install -r requirements.txt
  Insert file path in the first row of implement_interpolation.main() to a '*.vhdr' file in a folder containing it's mathcing '*.eeg' and '*.vmrk'
  Run implement_interpolation.py

# Files description
  'Area Mapping.txt'
      A list of all row indices with thier coresponding brain region
      
  'Research problem.docx'
      A one page description of this project's goals
      
  'draw_all.py'
      A code designed to create folders containing plots for each brain region seperatly: Complete trial, Pulses zoom out, (Pulse zoom in) * No. of pulses
      
  'get_interpolation improved'
      A code flow designated to find the location of the TMS pulses.
      Input: Raw object #current version creates raw object from hard-coded file path
      Output: List with pairs of indices ranging 20 time units. The indices between each pair are the indices which their values will be removed and replaced by interpolation
    
   'implement_interpolation.py'
      -The main flow- 
        Input: file path '*.vhdr' in a folder with '*.eeg' and '*.vmrk' #current version contains hard coded file path
        Creates raw object, calls 'get_interpolation_improved', creates the log, creates new interpolated matrix
        Output:
          Printed log of events and interesting/suspicious datapoints
          Plots of the interpolated EEG data
          New raw mne object containing the previous info and the new interpolated matrix
          
 # Links & Contacts:
    Jupiter: https://datalore.jetbrains.com/notebook/Bqm9dGwjGT5WNga8DL1wjR/SCHFsjVEM44pRsRA94YbNK
    amitomer312@gmail.com
    amithorovitz@mail.tau.ac.il
    matanshvide@mail.tau.ac.il
    
    
    

