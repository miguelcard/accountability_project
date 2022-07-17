import React from 'react';
import { Redirect, Route } from 'react-router';
import { isAuthentication } from '../data/auth/authentication';


export const PrivateRoute = ({ component, ...options }) => {
    const isAuth = isAuthentication()
    if (isAuth) return <Route {...options} component={component}/>
    return <Redirect to="/login"/>
}


export const PublicRoute = ({ component, ...options }) => {
    const isAuth = isAuthentication()
    if (!isAuth) return <Route {...options} component={component}/>
    return <Redirect to="/profile"/>
}
