# RALMAC
Registration-based Automated Lesion Matching and Correspondence

io.py
* sitk_image = read_dicom(dicom_path)

registration.py
* implements image registration
* transformation = register(sitk_fixed, sitk_moving)
* moved_image = transform_image(moving, transform)
* registered_coordinates = transform_coordinates(moving_coordinates,transform)

correspondence.py
* implements Hungarian algorithm
* correspondence_list = hungarian(fixed_coordinates, registered_coordinates)
* correspondence_list: set(G1,G2, ...)

