# RALMAC
Registration-based Automated Lesion Matching and Correspondence

inside repository root/RALMAC:

processing.py
* implements image preprocessing functions for registration

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
run_simulated_data.py
* import RALMAC

* load inputs: image_A, image_B, coordinate_list_A, coordinate_list_B
* run everything...
* outputs: [ (index of element in A A1,B1), (A2,B2), (None,B3), (A4,None) ] each element represetns unique lesion
  
* loads test dicom images, and coordinate lists
* runs RALMAC.registration
* runs RALMAC.transform_coordinates
* runs RALMAC.match


