import React, { Fragment } from 'react';
import profiles from '../data/profiles.json';
const images = require.context('../../public/assets/images', true);

const AboutUs = () => {
	return (
		//col-xs-12 col-sm-12 col-md-8 col-lg-8
		<>
			<div className='cw-section'>
				<div className='row'>
					{profiles && profiles.length
						? profiles.map((data) => {
								let image = images(`./${data.image}`);
								return (
									<div className=' mb-20 bio'>
										<div className='bio-details'>
											<h1>{data.name}</h1>
											<h3 className='job-title'>{data.title}</h3>
											<ul className='speaker-social'></ul>
											<p>{data.bio}</p>
										</div>
										<div className='bio-pic'>
											<img
												width='300'
												height='300'
												src={image}
												className='wp-post-image'
												alt=''
											/>
										</div>
									</div>
								);
						  })
						: null}
				</div>
			</div>
		</>
	);
};
export default AboutUs;
