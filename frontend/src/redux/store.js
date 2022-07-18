import {createStore, combineReducers, compose, applyMiddleware} from 'redux'
import thunk from 'redux-thunk'

import loginReducer, { restoreSessionAction, restoreDataUserIntoLocalStorage, restoreDataLanguageIntoLocalStorage, restoreUpdatedDataLanguageIntoLocalStorage } from './loginDucks'
import groupReducer, { getDataGroupsAction } from './groupsDucks'
import { restoreDataGroupIntoStorage } from './groupsDucks'


const rootReducer = combineReducers({
    dataLogin: loginReducer,
    groups: groupReducer
})


const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

export default function generateStore() {
    const store = createStore(
        rootReducer,
        composeEnhancers(applyMiddleware(thunk))
    )
    restoreDataUserIntoLocalStorage()(store.dispatch)
    restoreSessionAction()(store.dispatch)
    restoreDataLanguageIntoLocalStorage()(store.dispatch)
    restoreDataGroupIntoStorage()(store.dispatch)
    // getDataGroupsAction()(store.dispatch)
    // restoreUpdatedDataLanguageIntoLocalStorage()(store.dispatch)
    return store;
}