# RALMAC
Registration-based Automated Lesion Matching and Correspondence

inside repository root/RALMAC:

registration.py
* implements image registration
* transformation = register(sitk_fixed, sitk_moving)
* moved_image = transform_image(moving, transform)
* registered_coordinates = transform_coordinates(moving_coordinates,transform)

correspondence.py
* implements Hungarian algorithm
* correspondence_list = match(fixed_coordinates, registered_coordinates, threshold=2, ... )
* xyz = get_coordinates(lesion_name,coorespondence_list, fixed_coordaintes, registered_coordinates)
* correspondence_list: set{ dict{"name":"G1","fixed": [... indices of elements in fixed_coordinates list],"moving": [... indices of moving coordinates list...]}, dict({}) }
* correspondence_list [ [], [], [] ]

io.py
* sitk_image = read_dicom(dicom_path)

plots.py
* implements triplanar preview of registrations and matched lesions

inside repository root/examples:
run_{some data}.py
* import RALMAC
* loads test dicom images, and coordinate lists
* runs RALMAC.registration
* runs RALMAC.transform_coordinates
* runs RALMAC.match
