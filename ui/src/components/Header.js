//import React from 'react';
import React from 'react';

const Header = (props) => {
	return (
		<div className='cw-section cw-header mb-20' id='cw-scrollTop'>
			<div className='d-flex justify-content-between align-items-center col-sm-12'>
				<a href='/' className='cw-heading cw-heading--primary' title='COVID 19'>
					COVID 19
				</a>

				<a href='mailto:gahoba@gmail.com' className='cw-hading cw-heading--usermgmt' title='Email '>
					Email Us
				</a>
			</div>
		</div>
	);
};

export default Header;
