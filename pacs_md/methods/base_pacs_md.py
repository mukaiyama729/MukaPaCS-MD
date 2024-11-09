from core import *
from pacs_md.md import IMD
import shutil
from traj import TrajLoader, TrajSelector, AlignmentCreater, TrajTransformer, TrajAssembler
from models import MDResultModel, AnalyzedResultModel
from mdtraj import Trajectory, Topology
import mdtraj as md
import numpy as np
from numpy import ndarray
from file import FileCreater
import os, re, shutil
from multiprocessing import Pool
from typing import List, Dict, Tuple
from settings import Settings
import logging
import pickle
import copy

logger = logging.getLogger('pacs_md')
selection_logger = logging.getLogger('selection')

class BasePaCSMD:
    def __init__(self, trial: int, initial_file_pathes: Dict[str, str], files: List[str], work_dir: str, settings: Settings):
        self.initial_file_pathes = initial_file_pathes
        self.files = files
        self.work_dir = work_dir
        self.settings = settings
        self.cycle = 0
        self.rank_traj_list = []
        self.trial = trial

    def set_core(self, evaluater: IEvaluater, analyzer: IAnalyzer, selector: ISelector, visualizer: IVisualizer):
        logging.info('Set core')
        self.evaluater = evaluater
        self.analyzer = analyzer
        self.selector = selector
        self.visualizer = visualizer

    def set_md(self, md: IMD):
        logger.info('Set MD')
        self.md = md

    def set_reference_traj(self):
        loader = TrajLoader()
        loader.load(self.initial_file_pathes['input'])
        self.ref_traj: Trajectory = loader.trajectory
        logger.info('Set reference trajectory')

    def initial_md(self):
        logger.info('Initial MD')
        self.pacs_dir_pathes = []
        logger.info('pacs_dir_pathes: {}'.format(self.pacs_dir_pathes))
        logger.info('Create directories for PaCS')
        tpr_file_name = 'topol.tpr'
        creater = FileCreater(to_dir=self.work_dir)
        self.pacs_dir_pathes.append(creater.create_dir('pacs-0-0'))
        creater.change_to_dir(os.path.join(self.work_dir, 'pacs-0-0'))
        creater.copy_file(self.files['input'])
        creater.create_tpr_file(tpr_file_name, self.files, self.initial_file_pathes)

        self.md.set_input_dir(self.pacs_dir_pathes[0])
        self.md.set_output_dir(self.pacs_dir_pathes[0])

        if self.settings.use_gpu:
            self.md.single_md(1, self.settings.threads_per_process, self.settings.use_gpu)
        else:
            self.md.single_md(self.settings.process_per_node, self.settings.threads_per_process, self.settings.use_gpu)

    def _update_ranked_traj_list(self, analyzed_result_model) -> bool:
        self.rank_traj_list = self._select_structures(analyzed_result_model)

    def _execute_analyze(self):

        self.analyzer.set_md_result(self.md_result)
        self.analyzer.set_configuration(self.settings.core['analyzer'])
        analyed_result_model = self.analyzer.analyze()

        self.visualizer.set_analyzed_result_model(analyzed_result=analyed_result_model)
        self.visualizer.set_configuration(self.settings.core['visualizer'])
        self.visualizer.visualize()

        return analyed_result_model

    def _is_continued(self, analyed_result_model: AnalyzedResultModel):
        self.evaluater.set_analyzed_result_model(analyed_result_model)
        self.evaluater.set_configuration(self.settings.core['evaluater'])
        is_continue = self.evaluater.evaluate()
        return is_continue

    def _select_structures(self, analyed_result_model: AnalyzedResultModel):
        self.selector.set_analyzed_result_model(analyed_result_model)
        self.selector.set_configuration(self.settings.core['selector'])
        return self.selector.select()

    def make_traj_objs(self, dir_pathes: List[str]) -> Dict[Tuple[int, int, int], Trajectory]:
        trj_objs = {}
        pattern = r'-(\d+)-(\d+)'
        for dir_path in dir_pathes:
            match = re.search(pattern, dir_path)
            if match:
                cyc = int(match.group(1))
                rep = int(match.group(2))
                traj_file_path = os.path.join(dir_path, 'traj_comp_noPBC.xtc')
                gro_file_path = self.initial_file_pathes['input']
                loader = TrajLoader()
                loader.load(traj_file_path, gro_file_path)
                trj_objs[(self.trial, cyc, rep)] = loader.trajectory
        return trj_objs

    def create_md_result(self, traj_objs: Dict[Tuple[int, int, int], Trajectory]) -> MDResultModel:
        alignment_operators = self._create_alignment_operator(traj_objs, self.ref_traj)
        #logger.info('Alignment operators: {}'.format(alignment_operators))

        selected_trajs = self._select_traj(traj_objs)#self.ref_traj.topology
        #logger.info('Selected trajs: {}'.format(selected_trajs))

        transformed_traj_data = self._transform_traj(selected_trajs, alignment_operators)
        #logger.info('Transformed traj data: {}'.format(transformed_traj_data))

        assembled_traj_data = self._assemble_traj_data(transformed_traj_data)
        #logger.info('Assembled traj data: {}'.format(assembled_traj_data))

        self.md_result = self._get_md_result(assembled_traj_data)
        logger.info('md result: {}'.format(self.md_result))

        del alignment_operators, selected_trajs, transformed_traj_data, assembled_traj_data
        return self.md_result

    def _get_md_result(self, traj_data: Dict[Tuple[int, int, int, float], List[np.ndarray]]) -> MDResultModel:
        copied_traj_data = copy.deepcopy(traj_data)
        del traj_data
        return MDResultModel(result=copied_traj_data, current_state=(self.trial, self.cycle))

    def _assemble_traj_data(self, traj_data: Dict[Tuple[int, int, int], List[np.ndarray]]) -> Dict[Tuple[int, int, int, float], List[ndarray]]:
        self.traj_assembler = TrajAssembler(traj_data, max_length=self.settings.assemble_max_length)
        return self.traj_assembler.assemble(traj_data)

    def _select_traj(self, traj_data: Dict[Tuple[int, int, int], Trajectory]) -> Dict[Tuple[int, int, int], List[Trajectory]]:
        traj_selector = TrajSelector(traj_data)
        traj_selector.set_selects(self.settings.selects)
        return traj_selector.select()

    def _create_alignment_operator(self, traj_data: Dict[Tuple[int, int, int], Trajectory], ref_traj: Trajectory) -> Dict[Tuple[int, int, int, float], Tuple[ndarray, ndarray]]:
        alignment_creater = AlignmentCreater(traj_data)
        alignment_creater.set_ref_structure(ref_traj, ref_selection=self.settings.ref_selection)
        return alignment_creater.create()

    def _transform_traj(self, traj_objs: Dict[Tuple[int, int, int], List[Trajectory]], alignment_operators: Dict[Tuple[int, int, int, float], List[np.ndarray]]) -> Dict[Tuple[int, int, int, float], List[ndarray]]:
        traj_transformer = TrajTransformer(traj_objs)
        traj_transformer.transform(align_operator=alignment_operators)
        return traj_transformer.traj_data

    def create_traj_files(self, prallel=True):
        logger.info('Create trajectory files')
        if prallel:
            p = Pool(self.settings.total_processes)
            p.map(self._worker, self.pacs_dir_pathes)
            p.close()
        else:
            for pacs_dir_path in self.pacs_dir_pathes:
                FileCreater(to_dir=pacs_dir_path, from_dir=pacs_dir_path).create_noPBC_xtc(self.initial_file_pathes['index'])

    def _worker(self, pacs_dir_path):
        FileCreater(to_dir=pacs_dir_path, from_dir=pacs_dir_path).create_noPBC_xtc(self.initial_file_pathes['index'])

    def prepare_for_md(self):
        self.pacs_dir_pathes = FileCreater(self.work_dir).create_dirs_for_pacs('pacs-{}'.format(self.cycle), self.settings.nbins)
        chosen_dict = {}
        for index, pacs_path in enumerate(self.pacs_dir_pathes):
            trial, cyc, rep, time = self.rank_traj_list[index]
            chosen_dict[index] = {'next_path': pacs_path, 'cyc': cyc, 'rep': rep, 'time': time}
            creater = FileCreater(pacs_path, from_dir=self.cyc_rep_path(cyc, rep))
            creater.create_input_file(self.files, time)
            creater.create_tpr_file('topol.tpr', self.files, self.initial_file_pathes)
        selection_logger.info('Chosen dict: {}'.format(chosen_dict))

    def cyc_rep_path(self, cyc, rep):
        return os.path.join(self.work_dir, 'pacs-{}-{}'.format(cyc, rep))

    def parallel_md(self):
        self.md.multi_md(
            parallel=self.settings.parallel,
            multi_dir_pathes=self.pacs_dir_pathes,
            total_process=self.settings.total_processes,
            threads_per_process=self.settings.threads_per_process,
            use_gpu=self.settings.use_gpu
            )

    def execute(self):
        self.initial_md()
        self.create_traj_files(prallel=bool(self.settings.create_file_parallel))
        self.create_md_result(self.make_traj_objs(self.pacs_dir_pathes))
        analyzed_result_model = self._execute_analyze()
        self._update_ranked_traj_list(analyzed_result_model)
        self.cycle += 1
        while self.cycle <= self.settings.cycle_limit:
            try:
                self.prepare_for_md()
                self.parallel_md()
                self.create_traj_files(prallel=bool(self.settings.create_file_parallel))
                self.create_md_result(self.make_traj_objs(self.pacs_dir_pathes))
                analyzed_result_model = self._execute_analyze()
                is_continued = self._is_continued(analyzed_result_model)
                if not is_continued:
                    break
            except Exception as e:
                logger.error('Error: {}'.format(e))
                raise e
            self._update_ranked_traj_list(analyzed_result_model)
            self.cycle += 1
            self.save_instance()

    def restart(self):

        while self.cycle <= self.settings.cycle_limit:
            try:
                self.prepare_for_md()
                self.parallel_md()
                self.create_traj_files(prallel=True)
                self.create_md_result(self.make_traj_objs(self.pacs_dir_pathes))
                analyzed_result_model = self._execute_analyze()
                is_continued = self._is_continued(analyzed_result_model)
                if not is_continued:
                    break
            except Exception as e:
                logger.error('Error: {}'.format(e))
                raise e
            self._update_ranked_traj_list(analyzed_result_model)
            self.cycle += 1
            self.save_instance()

    def save_instance(self):
        pass
