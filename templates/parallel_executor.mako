<% unique_tasks = dict((task.name, task) for task in tasks).values() %>
%for task in unique_tasks:
void *_hook_${task.name}(void *args) {
  PyObject **py_args = (PyObject **) args;
  ${task.name}(${', '.join('py_args[%d]' % (ii,) for ii in range(len(task.args)))});
  return NULL;
}

%endfor
void execute(${', '.join(', '.join('PyObject *' + arg for arg in task.args) for task in tasks)}) {
  pthread_t threads[${len(tasks)}];
  void *(*thread_tasks[${len(tasks)}])(void *);
  PyObject **thread_args[${len(tasks)}];

  // Assign the thread tasks and bundle up the thread arguments.
%for ii, task in enumerate(tasks):
  thread_tasks[${ii}] = &_hook_${task.name};
  thread_args[${ii}] = (PyObject **) malloc(sizeof(PyObject *) * ${len(task.args)});
  %for jj, arg in enumerate(task.args):
  thread_args[${ii}][${jj}] = ${arg};
  %endfor

%endfor

  for (int ii = 0; ii < ${len(tasks)}; ii++) {
    pthread_create(&threads[ii], NULL, thread_tasks[ii], thread_args[ii]);
  }

  for (int ii = 0; ii < ${len(tasks)}; ii++) {
    pthread_join(threads[ii], NULL);
  }

  for (int ii = 0; ii < ${len(tasks)}; ii++) {
    free(thread_args[ii]);
  }
}
