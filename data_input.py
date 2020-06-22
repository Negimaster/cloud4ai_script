import sys
import os

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry
from msrest.authentication import ApiKeyCredentials

water_dict = {'endpoint': 'https://nm-c4ai-vision.cognitiveservices.azure.com/', 'access_key': '3415ff3b23bc4e56b8fd87a76fe81324', 'resource_id': '/subscriptions/dfaa49fb-c9a7-4004-bad7-38d51bf61c2b/resourceGroups/nicomem-cloud4ai/providers/Microsoft.CognitiveServices/accounts/nm-c4ai-vision', 'iteration_name': 'classifyWater', 'project_id': '72bed1b3-e704-44d6-a7f0-ed7138ec5cd4'}



def check_args(args):
    if len(args) != 2:
        print('Usage: python data_input.py path/to/directory {water / boat}')
        return 1

    if not os.path.isdir(args[0]):
        print(f'{args[0]} is not a directory')
        return 2

    if args[1] not in ['water', 'boat']:
        printf(f'Unrecognized option {args[1]}')
        return 3

    return 0

def get_resource_dict(option):
    if option == 'water':
        return water_dict
    elif option == 'boat':
        return boat_dict
    else:
        return {}

def is_image(path):
    extension = path.split('.')[-1]
    return extension in ['jpg', 'jpeg', 'png']

def main(args):
    status = check_args(args)
    if status != 0:
        return status

    resource_dict = get_resource_dict(args[1]) 
    
    credentials = ApiKeyCredentials(in_headers={"Training-key": resource_dict['access_key']})
    trainer = CustomVisionTrainingClient(resource_dict['endpoint'], credentials)

    directory = args[0]
    counter = 0
    image_list = []
    tags = trainer.get_tags(resource_dict['project_id'])
    tagnames = [tag.name for tag in tags]
    print(f'tags: {tagnames}')
    '''
    for root, _, filename in os.walk(directory):
        if not is_image(filename):
            print(f'Skipping {filename}')
            continue

        counter += 1

        fullpath = os.path.join(root, filename)
        with open(fullpath, 'rb') as image_content:
            image_list.append(ImageFileCreateEntry(name=filename, contents=image_content.read(), tags_id=[]))

        if counter == 64:
            #send
            image_list = []
            counter = 0

    if image_list
    '''
    return 0

if __name__ == '__main__':
    status = main(sys.argv[1:])
    exit(status)

