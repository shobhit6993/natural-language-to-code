trigger = {'id': 'facebook', 'conf': 0.8,
                'function':
                    {'id': 'upload_pic_area', 'conf': 0.5,
                        'fields': [
                            {'id': 'location', 'value': 'austin', 'conf': 1},
                            {'id': 'time', 'value': 'am', 'conf': 1}
                        ]
                    }
           }

action = {'id': 'google_drive', 'conf': 0.8,
                'function':
                    {'id': 'save', 'conf': 0.5,
                        'fields': [
                            {'id': 'filename', 'value': 'Message', 'conf': 0.8},
                            {'id': 'path', 'value': '/home/pics', 'conf': 1}
                        ]
                    }
          }


channel_template = {'id': "", 'conf': 0., 'function': {}}
function_template = {'id': "", 'conf': 0., 'fields': []}
field_template = {'id': "", 'value': "", 'conf': 0.}


# trigger = [{'id': 'facebook', 'conf': 0.8,
#                 'functions': [
#                     {'id': 'upload_pic_area', 'conf': 0.5,
#                         'fields': [
#                             {'id': 'location', 'value': 'austin', 'conf': 1},
#                             {'id': 'time', 'value': 'am', 'conf': 1}
#                         ]
#                     },
#                     {'id': 'upload_pic', 'conf': 0.5, 'fields': {}}
#                 ]
#         },
#         {'id': 'instagram', 'conf': 0.8,
#             'functions': [{'id': 'upload_pic', 'conf': 0.5, 'fields': {}}]
#         }]
#
# action = [{'id': 'google_drive', 'conf': 0.8,
#                 'functions': [
#                     {'id': 'save', 'conf': 0.5,
#                         'fields': [
#                             {'id': 'filename', 'value': 'Message', 'conf': 0.8},
#                             {'id': 'path', 'value': '/home/pics', 'conf': 1}
#                         ]
#                     }
#                 ]
#         }]
#
# channel_template = {'id': "", 'conf': 0., 'function': {}}
# function_template = {'id': "", 'conf': 0., 'fields': []}
# field_template = {'id': "", 'value': "", 'conf': 0.}
