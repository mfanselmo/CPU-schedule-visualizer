from backend.task import Task
from backend.processor import Processor


class Backend:
    """

    """

    def __init__(self, file_path):

        self.tasks = {}
        self.processors = {}

        self.file_path = file_path

        self._number_processors = None
        self._number_timestamps = None

        self.read_file()

    @property
    def number_processors(self):
        """
        calculates once the number of processors on the tasks
        """
        if self._number_processors:
            return self._number_processors

        uniques = set()

        for task in self.tasks.values():
            for job in task.jobs.values():
                for start in job.starts:
                    uniques.add(start['processor_id'])
                for finish in job.finishes:
                    uniques.add(finish['processor_id'])

        self._number_processors = len(uniques)
        return self._number_processors

    @property
    def number_timestamps(self):
        """
        calculates once the number of processors on the tasks
        """
        if self._number_timestamps:
            return self._number_timestamps

        max_ = -1

        for task in self.tasks.values():
            for job in task.jobs.values():
                if job.activation_ts > max_:
                    max_ = job.activation_ts
                if job.deadline_ts > max_:
                    max_ = job.deadline_ts
                for start in job.starts:
                    if start['timestamp'] > max_:
                        max_ = start['timestamp']
                for finish in job.finishes:
                    if finish['timestamp'] > max_:
                        max_ = finish['timestamp']

        self._number_timestamps = max_
        return self._number_timestamps

    def __getitem__(self, processor_id: str):
        """
        Allows us to get a processor with the syntax backend['1']
        Which allows us to get all events on a timestamp on a processor
        backend['1'][0] gets the events that happened on processor '1' in the timestamp 0
        """
        return self.processors[processor_id]

    def read_file(self):
        with open(self.file_path) as f:

            for line in f.readlines():
                self.process_line(line)

    def process_line(self, line):
        timestamp, task_id, job_id, processor_id, type_of_event, extra_data = line.split(",")

        data = {
            'timestamp': timestamp,
            'task_id': task_id,
            'job_id': job_id,
            'processor_id': processor_id,
            'type_of_event': type_of_event,
            'extra_data': extra_data
        }

        # get processor
        processor = None
        if processor_id != '0':
            if processor_id not in self.processors:
                processor = Processor(processor_id)
                self.processors[processor_id] = processor
            else:
                processor = self.processors[processor_id]

        if task_id == '0':
            # processor only event
            self.process_processor_only_event(data, processor)
        else:
            self.process_task_event(data, processor)

    def process_processor_only_event(self, data, processor):
        pass

    def process_task_event(self, data, processor):
        task_id = data['task_id']
        if task_id not in self.tasks:
            # Create new Task instance
            task = Task(task_id)
            self.tasks[task_id] = task
        else:
            task = self.tasks[task_id]

        task.add_job_info(data)
        if processor is not None:
            processor.add_task(task)
        else:
            Processor.processor_independant_tasks[task_id] = task

    def size_of_grid(self):
        return (self.number_timestamps*100+200, self.number_processors*100+200)
