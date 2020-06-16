//import React from 'react';
import React from 'react';

const Header = (props) => {
	return (
		<div className='cw-section cw-header mb-20' id='cw-scrollTop'>
			<div className='d-flex justify-content-between align-items-center col-sm-12'>
				<a href='/' className='cw-heading cw-heading--primary' title='COVID 19'>
					COVID 19
				</a>

				<a href='/' className='cw-hading cw-heading--usermgmt' title='Contact Us'>
					Contact Us
				</a>
			</div>
		</div>
	);
};

export default Header;
