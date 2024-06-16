from command import gmx_command
import os
import shutil
import logging
logger = logging.getLogger('pacs_md')

class FileCreater:
    def __init__(self, to_dir, from_dir=None):
        self.to_dir = to_dir
        self.from_dir = to_dir if from_dir == None else from_dir

    def create_tpr_file(self, tpr_file_name, initial_files: dict, initial_files_path):
        logger.info('Create tpr file')

        tpr_file_path = os.path.join(self.to_dir, tpr_file_name)

        count = 0
        while not os.path.exists(tpr_file_path):
            os.system(
                self.tpr_command(
                    tpr_file_name,
                    os.path.join(self.to_dir, initial_files['input']),
                    initial_files_path['topol'],
                    initial_files_path['index'],
                    os.path.join(self.to_dir, initial_files['input']),
                    initial_files_path['md']
                )
            )
            count += 1
            if count >= 10:
                raise FileExistsError('File already exists: {}'.format(tpr_file_path))

    def tpr_command(self, tpr_file_name, gro_file_path, top_file_path, index_file_path, ref_file_path, mdp_file_path):
        command = (
            gmx_command +
            ' grompp' +
            ' -f ' + mdp_file_path +
            ' -c ' + gro_file_path +
            ' -p ' + top_file_path +
            ' -n ' + index_file_path +
            ' -o ' + os.path.join(self.to_dir, tpr_file_name) +
            ' -r ' + ref_file_path +
            ' -maxwarn 10'
        )
        logger.info('Command: {}'.format(command))
        return command

    def create_input_file(self, initial_files, time):
        logger.info('Create input file')
        os.system(
            self.input_command(initial_files, time)
        )

    def input_command(self, initial_files, time):
        command = (
            "echo System | " + gmx_command +
            ' trjconv' +
            ' -f ' + os.path.join(self.from_dir, 'traj_comp_noPBC.xtc') +
            ' -s ' + os.path.join(self.from_dir, 'topol.tpr') +
            ' -o ' + os.path.join(self.to_dir, initial_files['input']) +
            ' -dump ' + str(float(time))
        )
        logger.info('Command: {}'.format(command))
        return command

    def create_noPBC_xtc(self, index_file_path, stdin='System'):
        command = (
            f"echo {stdin} | " + gmx_command +
            ' trjconv' +
            ' -f ' + os.path.join(self.from_dir, 'traj_comp.xtc') +
            ' -s ' + os.path.join(self.from_dir, 'topol.tpr') +
            ' -n ' + index_file_path +
            ' -o ' + os.path.join(self.to_dir, 'traj_comp_noPBC_mol.xtc') +
            ' -pbc mol'
        )
        logger.info('Command: {}'.format(command))
        os.system(command)

        second_command = (
            f"echo {stdin} | " + gmx_command +
            ' trjconv' +
            ' -f ' + os.path.join(self.to_dir, 'traj_comp_noPBC_mol.xtc') +
            ' -s ' + os.path.join(self.from_dir, 'topol.tpr') +
            ' -n ' + index_file_path +
            ' -o ' + os.path.join(self.to_dir, 'traj_comp_noPBC.xtc') +
            ' -pbc nojump'
        )
        logger.info('Command: {}'.format(second_command))
        os.system(second_command)
        os.remove(os.path.join(self.to_dir, 'traj_comp_noPBC_mol.xtc'))
        logger.info('Remove {}'.format(os.path.join(self.to_dir, 'traj_comp_noPBC_mol.xtc')))

    def create_dir(self, dir_name):
        path = os.path.join(self.to_dir, dir_name)
        os.makedirs(path, exist_ok=True)
        logger.info('Create directory: {}'.format(path))
        return path

    def create_dirs_for_pacs(self, dir_name, nbins) -> list:
        pathes = []
        for i in range(nbins):
            name = dir_name + '-{}'.format(i)
            pathes.append(self.create_dir(name))
        logger.info('Pathes: {}'.format(pathes))
        return pathes

    def change_from_dir(self, from_dir):
        self.from_dir = from_dir
        logger.info('Change from_dir: {}'.format(self.from_dir))

    def change_to_dir(self, to_dir):
        self.to_dir = to_dir
        logger.info('Change to_dir: {}'.format(self.to_dir))

    def copy_file(self, file_name):
        shutil.copy(os.path.join(self.from_dir, file_name), self.to_dir)
        logger.info('Copy {} to {}'.format(file_name, self.to_dir))
