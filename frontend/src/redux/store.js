import {createStore, combineReducers, compose, applyMiddleware} from 'redux'
import thunk from 'redux-thunk'

import loginReducer, { restoreSessionAction, restoreDataUserIntoLocalStorage, restoreDataLanguageIntoLocalStorage, restoreUpdatedDataLanguageIntoLocalStorage } from './loginDucks'


const rootReducer = combineReducers({
    dataLogin: loginReducer,
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
    // restoreUpdatedDataLanguageIntoLocalStorage()(store.dispatch)
    return store;
}