import axios from "axios"


//const
const initialState = {
    list: [],
    updatedList: [],
    fetching: false,
    loggedIn: false
}

const API = process.env.REACT_APP_API_REST


//types
const CREATE_SUCCESS_PROFILE_PHOTO = "CREATE_SUCCESS_PROFILE_PHOTO"
const GET_SUCCESS_DATA_LANGUAGES = "GET_SUCCESS_DATA_LANGUAGES"
const CREATE_SUCCESS_USER_DATA = "CREATE_SUCCESS_USER_DATA"
const GET_LOGIN_SUCCESS = 'GET_LOGIN_SUCCESS'
const RUNNING = 'RUNNING'
const GET_SUCCESS_REGISTER = 'GET_SUCCESS_REGISTER'
const GET_SUCCESS_LOGIN_FETCHING = 'GET_SUCCESS_LOGIN_FETCHING'
const LOGOUT_SUCCESS = 'LOGOUT_SUCCESS'
const TOTAL_LOGOUT_SUCCESS = 'TOTAL_LOGOUT_SUCCESS'
const GET_USER = "GET_USER"



//reducer
export const reducer = (state = initialState, action) => {
    switch (action.type) {
        case GET_USER:
            return {
                ...state,
                fetching: false,
                updatedList: action.payload
            }
        case GET_SUCCESS_DATA_LANGUAGES:
            return{
                ...state,
                languageList: action.payload,
                fetching: false
            }
        case CREATE_SUCCESS_USER_DATA:
            return {
                ...state,
                updatedList: action.payload,
                fetching: false
            }
        case CREATE_SUCCESS_PROFILE_PHOTO:
            return {
                ...state,
                updatedList: action.payload,
                fetching: false
            }
        case RUNNING:
            return {
                ...state,
                fetching: true
            }
        case GET_SUCCESS_REGISTER:
            return {
                ...state,
                list: action.payload,
                loggedIn: true,
                fetching: false
            }
        case GET_SUCCESS_LOGIN_FETCHING:
            return {
                ...state,
                fetching: true
            }
        case GET_LOGIN_SUCCESS:
            return {
                ...state,
                list: action.payload,
                loggedIn: true,
                fetching: false
            }
        case LOGOUT_SUCCESS:
            return {
                ...state
            }
        case TOTAL_LOGOUT_SUCCESS:
            return {
                ...initialState
            }
        default:
            return state
    }
}

export default reducer


//aux

export const searchingLanguage = (array, id) => {
    let result = array.filter(item => {
        return item.id === id
    })

    const totalRes = result.map(item => item.name)

    return totalRes
}

export const saveStorage = (storage) => {
    localStorage.storage = JSON.stringify(storage)
}

export const saveUserDataStorage = (store) => {
    localStorage.setItem('userUpdate', JSON.stringify(store))
}

export const saveStorageLanguages = (store) => {
    localStorage.setItem('languagesList', JSON.stringify(store))
}

const saveAnyThingInLocalStorage = (str, item) => {
    localStorage.setItem(str, JSON.stringify(item))
}

//actions for restore storage

export const restoreSessionAction = () => dispatch => {
    let store =  localStorage.getItem('storage')
    //convert to object
    store = JSON.parse(store)
    if (store && store.authentication.token) {
        dispatch({
            type: GET_LOGIN_SUCCESS,
            payload: store
        })
    }
}

export const restoreDataUserIntoLocalStorage = () => (dispatch) => {
    let store = localStorage.getItem('userUpdate')

    if (store == null) {
        dispatch({
            type: TOTAL_LOGOUT_SUCCESS
        })
    } else {
        const userData = JSON.parse(store)
        dispatch({
            type: GET_USER,
            payload: userData
        })
    }
}

export const restoreDataLanguageIntoLocalStorage = () => (dispatch) => {
    let store = localStorage.getItem('languagesList')

    const dataLanguages = JSON.parse(store)
    dispatch({
        type: GET_SUCCESS_DATA_LANGUAGES,
        payload: dataLanguages
    })
}

export const restoreUpdatedDataLanguageIntoLocalStorage = () => (dispatch) => {
    let newStore = localStorage.getItem('updatedNewLanguage')

    const dataUpdateLanguages = JSON.parse(newStore)
    dispatch({
        type: CREATE_SUCCESS_USER_DATA,
        payload: dataUpdateLanguages
    })
}


//actions


export const logoutAction = (token) => async (dispatch) => {
    dispatch({
        type: GET_SUCCESS_LOGIN_FETCHING
    })
    const lastData = await new Promise((resolve, reject) => {
        const config = {
            headers: {
                "Authorization": `token ${token}`,
            },
        }
        axios.post(`${API}/api/v1/logout/`, null, config)
        .then(res => {
            // console.log(res.data)
            resolve(res.data)
            dispatch({
                type: LOGOUT_SUCCESS
            })
        })
        .catch(error => {
            reject(error)
            console.log(error)
    })})
    // localStorage.removeItem('storage')
    // console.log(lastData)
    return lastData
}


export const sendUpdatedLanguages = (token, idLanguage) => async (dispatch) => {

    const bodyFormData = new FormData()
    bodyFormData.append('languages', idLanguage)

    dispatch({
        type: RUNNING
    })

    const successData = await new Promise((returnData, returnError) => {

        axios({
            headers: {
                "Authorization": `token ${token}`,
            },
            method: 'PUT',
            url: `${API}/api/v1.1/user/`,
            data: bodyFormData
        })
        .then(res => {
            console.log(res.data)
            returnData(res)
            dispatch({
                type: CREATE_SUCCESS_USER_DATA,
                payload: res.data
            })
            saveAnyThingInLocalStorage('updatedNewLanguage', res.data)
        })
        .catch(error => {
            console.log(error)
            returnError(error)
        })
    })
    return successData

}


export const sendDataLoginAction = (bodyFormData) => async (dispatch) => {

    dispatch({
        type: GET_SUCCESS_LOGIN_FETCHING
    })

    const ultimateData = await new Promise((resolve, reject) => {
        axios({
            method: 'POST',
            url: `${API}/api/v1/login/`,
            data: bodyFormData,
        })
        .then(res => {
            console.log(res.data)
            resolve(res)
            dispatch({
                type:GET_LOGIN_SUCCESS,
                payload: res.data
            })
            // saveStorage(getState())
        })
        .catch(error => {
            console.log(error)
            reject(error)
        })}
    )
    saveStorage(ultimateData.data)
    console.log(ultimateData)
    return ultimateData

}



export const sendDataRegisterAction = (bodyData) => async (dispatch) => {

    dispatch({
        type: RUNNING
    })

    const totalData = await new Promise((DataReturn, errorReturn) => {
        axios({
            method: 'POST',
            url: `${API}/api/v1/register/`,
            data: bodyData
        })
        .then(res => {
            // console.log(res)
            DataReturn(res)
            dispatch({
                type: GET_SUCCESS_REGISTER,
                payload: res.data
            })
        })
        .catch(error => {
            console.log(error)
            errorReturn(error)
        })
    })

    // console.log(totalData)
    saveStorage(totalData.data)
    return totalData
}

export const sendProfilePhotoAction = (bodyFormData, token) => async (dispatch) => {

    dispatch({
        type: RUNNING
    })

    const successData = await new Promise((returnData, returnError) => {
        axios({
            headers: {
                "Authorization": `token ${token}`,
            },
            method: 'PUT',
            url: `${API}/api/v1.1/user/`,
            data: bodyFormData
        })
        .then(res => {
            console.log(res)
            returnData(res)
            dispatch({
                type: CREATE_SUCCESS_PROFILE_PHOTO,
                payload: res.data
            })
        })
        .catch(error => {
            console.log(error)
            returnError(error)
        })
    })
    return successData
}

export const getDataLanguages = (token) => async (dispatch) => {
    dispatch({
        type: RUNNING
    })

    const successData = await new Promise((returnData, returnError) => {
        const config = {
            headers: {
                "Authorization": `token ${token}`,
            },
        }
        axios.get(`${API}/api/v1/users/languages/`, config)
        .then(res => {
            console.log(res.data);
            returnData(res.data)
            dispatch({
                type: GET_SUCCESS_DATA_LANGUAGES,
                payload: res.data
            })
        })
        .catch(error => {
            console.log(error)
            returnError(error)
        })
    })
    saveStorageLanguages(successData)
    return successData
}

export const sendAnyUserData = (userFormData, token) => async (dispatch) => {
    dispatch({
        type: RUNNING
    })

    const totalRes = await new Promise((returnData, returnError) => {
        const config = {
            headers: {
                "Authorization": `token ${token}`,
            },
        }
        axios.put(`${API}/api/v1.1/user/`, userFormData, config)
        .then (res => {
            console.log(res.data)
            returnData(res)
            dispatch({
                type: CREATE_SUCCESS_USER_DATA,
                payload: res.data
            })
        })
        .catch(error => {
            returnError(error)
        })
    })

    return totalRes
}


export const getUserDataAction = (token) => (dispatch) => {
    dispatch({
        type: RUNNING
    })
    const config = {
        headers: {
            "Authorization": `token ${token}`,
        },
    }
    axios.get(`${API}/api/v1.1/user/`, config)
    .then(res => {
        dispatch({
            type: GET_USER,
            payload: res.data
        })
        saveUserDataStorage(res.data)
    })
    .catch(error => {
        console.log(error.data)
    })
}