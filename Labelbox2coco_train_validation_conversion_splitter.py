import datetime as dt
from typing import Any, Dict
import json
import os
import logging
from PIL import Image
import requests
from shutil import copyfile

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def add_label(
        coco: Dict[str, Any], label_id: str, image_url: str,
        labels: Dict[str, Any]):
    """Incrementally updates COCO export data structure with a new label.

    Args:
        coco: The current COCO export, will be incrementally updated by this method.
        label_id: ID for the instance to write
        image_url: URL to download image file from
        labels: Labelbox formatted labels to use for generating annotation
    Returns:
        The updated COCO export represented as a dictionary.
    """
    image_url = image_url.strip()
    image = {
        "id": len(coco['images']) + 1,
        "file_name": image_url,
        "license": None,
        "flickr_url": image_url,
        "coco_url": image_url,
        "date_captured": None,
    }
    image['width'], image['height'] = Image.open('F:/New_Dataset/Converters/Data_Converter_Labelbox_json/data/'+image_url).size
    coco['images'].append(image)
    if not callable(getattr(labels, 'keys', None)):
        return
    objects = labels['objects']
    try:
        for x in objects:
            category_id = [y['id'] for y in coco['categories'] if y['name'] == x['title'].lower()]
            category_id = category_id[0]
            annotation = {
                "id": len(coco['annotations']) + 1,
                "image_id": image['id'],
                "category_id": category_id,
                "segmentation": [[x['bbox']['left'], x['bbox']['top'], x['bbox']['left'] + x['bbox']['width'],x['bbox']['top'] ,
                                  x['bbox']['left'] + x['bbox']['width'],x['bbox']['top'] + x['bbox']['height'], x['bbox']['left'],x['bbox']['top'] + x['bbox']['height'] ]],
                "area": x['bbox']['width']*x['bbox']['height'],  # float
                "bbox": [x['bbox']['left'], x['bbox']['top'], x['bbox']['left'] + x['bbox']['width'], x['bbox']['top'] +
                         x['bbox']['height']],
                "iscrowd": 0
            }
            coco['annotations'].append(annotation)
    except IndexError as I:
        print('Index Error',objects,category_id)


def from_json_coco(labeled_data,src_img,train_valid_counter):
    "Writes labelbox JSON export into MS COCO format."
    # read labelbox JSON output
    with open(labeled_data, 'r') as file_handle:
        label_data = json.loads(file_handle.read())
    # setup COCO dataset container and info
    #train / test
    counter = 0
    coco_train = make_coco_metadata(label_data[0]['Project Name'], label_data[0]['Created By'],)
    coco_val = make_coco_metadata(label_data[0]['Project Name'], label_data[0]['Created By'], )
    coco_train['licenses'] = {"id": 1, "name": None, "url": None}
    coco_val['licenses'] = {"id": 1, "name": None, "url": None}
    counter_categories = False
    os.makedirs(os.path.join(os.getcwd(),'datasets','train') ,exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), 'datasets', 'valid'), exist_ok=True)
    for data in label_data:
        # Download and get image name
        if not counter_categories:
            create_categories(data['Label']['objects'],coco_train)
            create_categories(data['Label']['objects'], coco_val)
            counter_categories = True
        try:
            if counter >= train_valid_counter :
                if len(data['Label']) > 0 :
                    add_label(coco_train, data['ID'], data['External ID'], data['Label'])
                    copyfile(src_img+data['External ID'], os.path.join(os.getcwd(),'datasets','train')+'\\'+data['External ID'])
                    counter +=1
            else:
                if len(data['Label']) > 0 :
                    add_label(coco_val, data['ID'], data['External ID'], data['Label'])
                    copyfile(src_img+data['External ID'], os.path.join(os.getcwd(),'datasets','valid')+'\\'+data['External ID'])
                    counter +=1

        except requests.exceptions.MissingSchema as exc:
            LOGGER.warning(exc)
            continue
        except requests.exceptions.ConnectionError:
            LOGGER.warning('Failed to fetch image from %s, skipping', data['Labeled Data'])
            continue
        except FileNotFoundError:
            print('File not found',data['External ID'])
            continue
        except KeyError:
            print('Keyerror' , data)

    path_data = os.path.join(os.getcwd(),'datasets','annotations')
    os.makedirs(path_data, exist_ok=True)

    with open(path_data+'//'+'instances_train.json', 'w+') as file_handle:
        print(data['External ID'])
        file_handle.write(json.dumps(coco_train))

    with open(path_data+'//'+ 'instances_val.json', 'w+') as file_handle:
        print(data['External ID'])
        file_handle.write(json.dumps(coco_val))

def create_categories(iter_cat , coco):
    id = 1
    for x in iter_cat:
        category = {}
        category["id"] = id
        category["name"] = x['title']
        category['supercategory'] = None
        coco['categories'].append(category)
        id+=1

def make_coco_metadata(project_name: str, created_by: str) -> Dict[str, Any]:
    """Initializes COCO export data structure.

    Args:
        project_name: name of the project
        created_by: email of the project creator

    Returns:
        The COCO export represented as a dictionary.
    """
    return {
        'info': {
            'year': dt.datetime.now(dt.timezone.utc).year,
            'version': None,
            'description': project_name,
            'contributor': created_by,
            'url': 'labelbox.com',
            'date_created': dt.datetime.now(dt.timezone.utc).isoformat()
        },
        'images': [],
        'annotations': [],
        'licenses': [],
        'categories': []
    }


if __name__ == '__main__':
    # Input File Name
    file_input = 'export-2020-XX-XXXXX_XX_XX.XXXX.json'
    Folder_to_pick_image_from = 'Path_2_data'
    valid_counter = 400 # Splitting the data into validation dataset and training dataset
    # Folder Name
    from_json_coco(file_input, Folder_to_pick_image_from,valid_counter)
