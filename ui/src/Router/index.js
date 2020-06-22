import React from 'react';
import { BrowserRouter, Switch, Route } from 'react-router-dom';
import Header from '../components/Header';
import AboutUs from '../components/AboutUs';
import AppContent from '../components/AppContent';
import Notfound from '../components/Notfound';

const AppRouter = () => {
	return (
		<BrowserRouter>
			<Header />
			<Switch>
				<Route exact={true} path='/'>
					<AppContent />
				</Route>
				<Route exact={true} path='/aboutus'>
					<AboutUs />
				</Route>
				<Route>
					<Notfound />
				</Route>
			</Switch>
		</BrowserRouter>
	);
};

export default AppRouter;
