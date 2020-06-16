import React from 'react';

const Loader = (props) => {
	return (
		<div className='cw-loader'>
			<div className='d-flex justify-content-center'>
				<div className='spinner-border cw-color--primary' role='status'>
					<span className='sr-only'>Loading...</span>
				</div>
			</div>
		</div>
	);
};
export default Loader;
