# Labelbox2coco
Have written a script to convert data from export of Labelbox (.json) { Refer the site here --> https://labelbox.com/ } into coco dataset {Reference :- https://cocodataset.org/#format-data}.


I have written this for object detection Data Format.

Key Points:- 

--> Input :-
          1.file_input :- Json file from labelbox eg 'export-2020-XX-XXXXX_XX_XX.XXXX.json'
          2.Folder_to_pick_image_from :- Folder where all the images of your dataset is present.(Please give the full path)
          3.valid_counter :- No of images you want to use for validation rest will be used for creating the training set.
          

