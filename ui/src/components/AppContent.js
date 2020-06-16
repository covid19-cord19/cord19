import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import axios from 'axios';
import taskData from '../data/tasks.json';
import ShowMoreText from 'react-show-more-text';

import Loader from './Loader';

const AppContent = () => {
	let [tasks, setTasks] = useState([]);
	let [subtasks, setSubTasks] = useState([]);
	let [selectedTask, setselectedTask] = useState({ label: '', value: '' });
	let [selectedSubtask, setselectedSubtask] = useState({ label: '', value: '' });
	let [showLoader, setShowLoader] = useState(false);
	let [responseData, setresponseData] = useState([]);

	let defaultTask = {
		value: 'Task1',
		label:
			'What do we know about vaccines and therapeutics? What do we know about vaccines and therapeutics? What has been published concerning research and development and evaluation efforts of vaccines and therapeutics?',
	};

	useEffect(() => {
		_getTasks();
	}, []);

	const _getTasks = () => {
		let tasks = taskData.map((data) => ({ label: data.label, value: data.value }));
		setTasks(tasks);
		_getSubTasks(defaultTask);
	};

	const _getSubTasks = (selectedOption) => {
		setselectedTask(selectedOption);
		let task = selectedOption.value;
		let subtasks = taskData.filter((data) => data.value === task);
		setSubTasks(subtasks[0].subtasks);
	};

	const _getData = (subtask) => {
		setselectedSubtask(subtask);
		setShowLoader(true);
		axios({
			method: 'post',
			url: 'http://34.223.223.77:4004/search',
			headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
			data: {
				task: selectedTask.label,
				subtask: subtask.label,
			},
		}).then((response) => {
			let responseData = response.data;
			setresponseData(responseData);
			setShowLoader(false);
		});
	};
	const _executeOnClick = (isExpanded) => {
		console.log(isExpanded);
	};

	return (
		<div className='col-sm-12'>
			<div className='cw-section'>
				<div className='row'>
					<div className='form-group'>
						<Select
							name={'Task'}
							label={'Task'}
							placeholder={'Select task'}
							options={tasks}
							onChange={_getSubTasks}
							value={selectedTask && selectedTask.value ? selectedTask : defaultTask}
						/>
					</div>
				</div>
				<div className='row'>
					<div className='form-group'>
						<Select
							name={'SubTask'}
							label={'SubTask'}
							placeholder={'Select subtask'}
							options={subtasks}
							onChange={_getData}
							value={selectedSubtask && selectedSubtask.value ? selectedSubtask : null}
						/>
					</div>
				</div>
			</div>
			{showLoader ? <Loader /> : null}
			{responseData && responseData.length
				? responseData.map((data, index) => {
						return (
							<div className='cw-section mb-30' key={index}>
								<div className='cols-sm-12'>
									<div className='row d-flex flex-column justify-content-left item p-20'>
										<div className='item-title mb-10'>
											<span>{responseData[index]['title'][0]}</span>
										</div>
										<div className='item-similairy-score mb-10'>
											<span>
												<b>Authors: </b>
											</span>
											<span></span>
										</div>
										<div className='item-similairy-score mb-10'>
											<span>
												<b>Similarity: </b>
											</span>
											<span>{responseData[index]['score']}</span>
										</div>
										<div className='item-description mb-10'>
											<ShowMoreText
												lines={3}
												more='Show more'
												less='Show less'
												anchorClass=''
												onClick={_executeOnClick}
												expanded={false}>
												{responseData[index]['body']}
											</ShowMoreText>
										</div>
										<div className='item-url mb-10'>
											{responseData[index]['url'] && responseData[index]['url'].length
												? responseData[index]['url'][0].split(';').map((data, index) => {
														return (
															<div>
																<a href={data} target='_blank'>
																	{data}
																</a>
															</div>
														);
												  })
												: ''}
										</div>
									</div>
								</div>
							</div>
						);
				  })
				: null}
		</div>
	);
};

export default AppContent;
