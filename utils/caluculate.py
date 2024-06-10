import numpy as np

class Calculater:

    def alignment(target_vec, rotation_matrix, translation_vector) -> np.ndarray:
        transformed_vec = np.matmul(target_vec, rotation_matrix.T) + translation_vector
        return transformed_vec

    def calculate_rmsd(self, coord1, coord2):
        diff = coord1 - coord2
        rmsd = np.sqrt(np.mean(np.sum(diff**2, axis=1)))
        return rmsd

    def superimpose_coordinates(self, coord1, coord2):
        center1 = np.mean(coord1, axis=0)
        center2 = np.mean(coord2, axis=0)
        coord1_centered = coord1 - center1
        coord2_centered = coord2 - center2

        covariance_matrix = np.dot(coord1_centered.T, coord2_centered)
        v, s, u = np.linalg.svd(covariance_matrix)
        dim = coord1.shape[1]
        diag_list = [1 for i in range(dim - 1)]
        diag_list.append(np.linalg.det(np.dot(v,u)))

        rotM = np.dot(v, np.dot(np.diag(diag_list), u))

        rotated_center = np.dot(rotM, center2.T).T
        translation_vec = center1 - rotated_center
        transformed_coord = np.dot(rotM, coord2.T).T + translation_vec

        return transformed_coord, (rotM, translation_vec)
