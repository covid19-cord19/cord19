//import React from 'react';
import React from 'react';
import { NavLink } from 'react-router-dom';

const Header = (props) => {
	return (
		<div className='cw-section cw-header mb-20' id='cw-scrollTop'>
			<div className='d-flex justify-content-between align-items-center col-sm-12'>
				<div>
					<NavLink className='cw-heading cw-heading--primary' to={'/'}>
						COVID 19
					</NavLink>
				</div>
				<div>
					<span className='mr-10'>
						<NavLink className='cw-hading cw-heading--links mr-10' to={'/aboutus'}>
							About Us
						</NavLink>
					</span>
					<span>
						<a href='mailto:gahoba@gmail.com' className='cw-hading cw-heading--links' title='Email '>
							Email Us
						</a>
					</span>
				</div>
			</div>
		</div>
	);
};

export default Header;
