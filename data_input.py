import sys
import os

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry
from msrest.authentication import ApiKeyCredentials

water_dict = {'endpoint': 'https://nm-c4ai-vision.cognitiveservices.azure.com/', 'access_key': '3415ff3b23bc4e56b8fd87a76fe81324', 'resource_id': '/subscriptions/dfaa49fb-c9a7-4004-bad7-38d51bf61c2b/resourceGroups/nicomem-cloud4ai/providers/Microsoft.CognitiveServices/accounts/nm-c4ai-vision', 'iteration_name': 'classifyWater', 'project_id': '72bed1b3-e704-44d6-a7f0-ed7138ec5cd4'}

boat_dict = {'endpoint': 'https://nm-c4ai-vision.cognitiveservices.azure.com/', 'access_key': '3415ff3b23bc4e56b8fd87a76fe81324', 'resource_id': '/subscriptions/dfaa49fb-c9a7-4004-bad7-38d51bf61c2b/resourceGroups/nicomem-cloud4ai/providers/Microsoft.CognitiveServices/accounts/nm-c4ai-vision', 'iteration_name': 'detectBoat', 'project_id': '8947e07b-6937-4e03-96b0-d802c62b8928'}


def check_args(args):
    if len(args) != 2 and len(args) != 3:
        print('Usage: python data_input.py path/to/directory {water / boat} [tag[,tag[,tag[,...]]]]')
        print(f'Gave {len(args)} args')
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

def get_correct_tags(tag_str, resource_dict, trainer):
    existing_tags = trainer.get_tags(resource_dict['project_id'])
    tags_str = tag_str.split(',')
    tag_list = []
    for tag_name in tags_str:
        found = False
        for tag_candidate in existing_tags:
            if tag_candidate.name == tag_name:
                tag_list.append(tag_candidate)
                found = True
                break
        if not found:
            return [], existing_tags

    return tag_list, existing_tags

def main(args):
    status = check_args(args)
    if status != 0:
        return status

    directory = args[0]
    water_or_boat = args[1]
    tag_str = ''
    has_tags = len(args) == 3
    if has_tags:
        tag_str = args[2]

    resource_dict = get_resource_dict(water_or_boat) 

    credentials = ApiKeyCredentials(in_headers={"Training-key": resource_dict['access_key']})
    trainer = CustomVisionTrainingClient(resource_dict['endpoint'], credentials)

    counter = 0
    image_list = []
    tag_ids = []

    if has_tags:
        tags, existing_tags = get_correct_tags(tag_str, resource_dict, trainer)
        if not tags:
            tags_names = [tag_it.name for tag_it in existing_tags]
            print(f'unrecognized tag {tag_str}')
            print(f'Choose among {tags_names}')
            return 4
        tag_ids = [tag.id for tag in tags]

    with os.scandir(directory) as dir_it:
        for entry in dir_it:
            
            if not entry.is_file():
                print(f'Skipping not file {entry.name}')
                continue

            counter += 1

            filename = entry.path

            with open(filename, 'rb') as image_content:
                image_list.append(ImageFileCreateEntry(name=filename, contents=image_content.read(), tag_ids=tag_ids))

            if counter == 64:
                print('Limit (64)Sending batch')
                upload_result = trainer.create_images_from_files(resource_dict['project_id'], images=image_list)
                if not upload_result.is_batch_successful:
                    print('Failed to send batch')
                    for image in upload_result.images:
                        print('Image status: ', image.status)
                    return 1
                image_list = []
                counter = 0


        if image_list:
            print('Sending last batch')
            upload_result = trainer.create_images_from_files(resource_dict['project_id'], images=image_list)
            if not upload_result.is_batch_successful:
                print('Failed to send batch')
            for image in upload_result.images:
                print('Image status: ', image.status)
    return 0

if __name__ == '__main__':
    status = main(sys.argv[1:])
    exit(status)
