import React from 'react'
import { Redirect, Route, Switch } from 'react-router'
import { isAuthentication } from '../data/auth/authentication'
import { PrivateRoute, PublicRoute } from './helperRoutes'
import HomeView from '../views/homeView'
import ProfileView from '../views/profileView'
import LoginView from '../views/loginView'
import RegisterView from '../views/registerView'



const Routes = () => {
    const isAuth = isAuthentication()
    return (
        <Switch>
            <Route exact path="/" component={HomeView}/>
            <PublicRoute exact path="/login" component={LoginView}/>
            <PublicRoute exact path="/register" component={RegisterView}/>
            <PrivateRoute exact path="/profile" component={ProfileView}/>
            {/* layout just has the header and the footer and in between renders any component you put */}
            {/* <Layaout> */}
                {/* <PrivateRoute exact path="/dashboard" component={Dashboard}/> */}
            {/* </Layaout> */}
            <Route exact path="*" render={() => {
                return <Redirect to={ isAuth ? '/profile': '/login' } />
            }} />
        </Switch>
    )
}

export default Routes
