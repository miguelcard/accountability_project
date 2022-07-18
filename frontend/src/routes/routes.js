import React from 'react'
import { Redirect, Route, Switch } from 'react-router'
import { isAuthentication } from '../data/auth/authentication'
import { PrivateRoute, PublicRoute } from './helperRoutes'
import HomeView from '../views/homeView'
import Test from './test'
import ProfileView from '../views/profileView'
import GroupsView from '../views/groupsView'
import Group from '../components/Groups/group'
import LoginView from '../views/loginView'
import RegisterView from '../views/registerView'
import Dashboard from '../components/dashboard'
import Layaout from '../containers/layaout'



const Routes = () => {
    const isAuth = isAuthentication()
    return (
        <Switch>
            <Route exact path="/" component={HomeView}/>
            <PublicRoute exact path="/login" component={LoginView}/>
            <PublicRoute exact path="/register" component={RegisterView}/>
            <PrivateRoute exact path="/profile" component={ProfileView}/>
            <Layaout>
                <PrivateRoute exact path="/dashboard" component={Dashboard}/>
            </Layaout>
            <Route exact path="/test" component={Test} />
            <PrivateRoute exact path="/groups" component={GroupsView}/>
            <PrivateRoute exact path="/groups/:id" component={Group}/>
            <Route exact path="*" render={() => {
                return <Redirect to={ isAuth ? '/profile': '/login' } />
            }} />
        </Switch>
    )
}

export default Routes
