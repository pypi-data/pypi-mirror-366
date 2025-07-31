import json
import os
import datetime
from PIL import Image

def create_cocodata():
    cocodata = dict()
    cocodata['info'] = {    
        "description":  "Rendered.AI Synthetic Dataset",
        "url":          "https://rendered.ai/",
        "contributor":  "info@rendered.ai",
        "version":      "1.0",
        "year":         str(datetime.datetime.now().year),
        "date_created": datetime.datetime.now().isoformat()}
    cocodata['licenses'] = [{
        "id":   0,
        "url":  "https://rendered.ai/",     # "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "name": "Rendered.AI License"}]     # "name": "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License"}]
    cocodata['images'] = list()
    cocodata['categories'] = list()
    return cocodata


def convert_coco(datadir, outdir, mapping = None):

    annsdir = os.path.join(datadir, "annotations")
    metadir = os.path.join(datadir, "metadata")
    imgdir = os.path.join(datadir, "images")
    annsfiles = os.listdir(annsdir)
    
    cocodata = create_cocodata()
    cats = {0:[None, 'coco_background']}
    imgid = 0
    annid = 0

    with open(os.path.join(outdir,'coco.json'), 'w+') as of:
        of.write('{"annotations": [')
        first = True

        # for each interpretation, gather annotations and map categories
        for f in sorted(annsfiles):
            if not f.endswith('.json'):
                continue
            with open(os.path.join(annsdir,f), 'r') as af: anns = json.load(af)
            with open(os.path.join(metadir,f.replace('ana','metadata')), 'r') as mf: metadata = json.load(mf)
            
            # for each object in the metadata file, check if any of the properties are true
            for obj in metadata['objects']:
                if mapping is None:
                    for ann in anns['annotations']:
                        if ann['id'] == obj['id']:
                            if [None, obj['type']] in cats.values(): class_num = [k for k,v in cats.items() if v == [None, obj['type']]][0]
                            else : class_num = len(cats.keys())
                            cats[class_num] = [None, obj['type']]
                            annotation = {}
                            annotation['id'] = annid
                            annotation['image_id'] = imgid
                            annotation['category_id'] = class_num
                            annotation['segmentation'] = ann['segmentation']
                            annotation['area'] = ann['bbox'][2] * ann['bbox'][3]
                            annotation['bbox'] = ann['bbox']
                            annotation['iscrowd'] = 0
                            annid += 1
                            if not first: of.write(', ')
                            json.dump(annotation, of)
                            first = False
                            break
                else:
                    for prop in mapping['properties']:
                        if eval(prop):
                            for ann in anns['annotations']:
                                if ann['id'] == obj['id']: 
                                    class_num = mapping['properties'][prop]
                                    cats[class_num] = mapping['classes'][class_num]
                                    annotation = {}
                                    annotation['id'] = annid
                                    annotation['image_id'] = imgid
                                    annotation['category_id'] = class_num
                                    annotation['segmentation'] = ann['segmentation']
                                    annotation['area'] = ann['bbox'][2] * ann['bbox'][3]
                                    annotation['bbox'] = ann['bbox']
                                    annotation['iscrowd'] = 0
                                    annid += 1
                                    if not first: of.write(', ')
                                    json.dump(annotation, of)
                                    first = False
                                    break
            
            date = datetime.datetime.now().isoformat()
            if 'date' in metadata: date = metadata['date']
            imgdata = {
                'id':               imgid, 
                'file_name':        metadata['filename'], 
                'date_captured':    date, 
                'license':          0 
            }
            try:
                imgdata['width'] = metadata['sensor']['resolution'][0]
                imgdata['height'] = metadata['sensor']['resolution'][1]
            except:
                im = Image.open(os.path.join(imgdir, anns['filename']))
                width, height = im.size
                imgdata['width'] =  width
                imgdata['height']=  height
            cocodata['images'].append(imgdata)
            imgid += 1
        sorted_cats = dict(sorted(cats.items()))
        for class_num, cat in sorted_cats.items():
            if class_num == 0: continue
            cocodata['categories'].append({
                'id':               class_num, 
                'name':             cat[-1],
                'supercategory':    cat[0]
            })

        of.write('], ')
        of.write(f'"info": {json.dumps(cocodata["info"])}, ')
        of.write(f'"licenses": {json.dumps(cocodata["licenses"])}, ')
        of.write(f'"images": {json.dumps(cocodata["images"])}, ')
        of.write(f'"categories": {json.dumps(cocodata["categories"])}')
        of.write('}')