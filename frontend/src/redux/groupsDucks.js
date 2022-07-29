import axios from 'axios'


//const
const initialData = {
    dataGroups: [],
    fetching: false,
    addUserIntoGroup: []
}
const API = process.env.REACT_APP_API_REST


//types
const GET_SUCCESS_GROUPS = 'GET_SUCCESS_GROUPS'
const GET_SUCCESS_FETCHING_GROUPS = 'GET_SUCCESS_FETCHING_GROUPS'
const GET_SUCCESS_CREATED = 'GET_SUCCESS_CREATED'
const GET_DATA_ERROR = 'GET_DATA_ERROR'
const GET_SUCCESS_CREATED_GROUP = 'GET_SUCCESS_CREATED_GROUP'



//reducer
const reducer = (state = initialData, action) => {
    switch (action.type) {
        case GET_SUCCESS_FETCHING_GROUPS:
            return {
                ...state,
                fetching: true
            }
        case GET_SUCCESS_GROUPS:
            return {
                ...state,
                dataGroups: action.payload,
                fetching: false
            }
        case GET_SUCCESS_CREATED_GROUP:
            return {
                ...state,
                createdGroup: action.payload,
                fetching: false
            }
        case GET_DATA_ERROR:
            return {
                ...state,
                addUserIntoGroup: action.payload
            }
        case GET_SUCCESS_CREATED:
            return {
                ...state,
                addUserIntoGroup: action.payload,
                fetching: false
            }
        default:
            return state
    }
}

export default reducer


//aux

const saveDataStorage = (store) => {
    localStorage.setItem('localGroup', JSON.stringify(store))
}


//actions

export const restoreDataGroupIntoStorage = () => (dispatch) => {
    let store = localStorage.getItem('localGroup')

    if (store == null) {
        store = [];
        dispatch({
            type: GET_DATA_ERROR,
            payload: store
        })
    }else {
        const dataGroup = JSON.parse(store)
        dispatch({
            type: GET_SUCCESS_CREATED,
            payload: dataGroup
        })
    }
}



export const getDataGroupsAction = () => (dispatch, getState) => {
    dispatch({
        type: GET_SUCCESS_FETCHING_GROUPS
    })
    axios.get(`${API}/api/v1/groups/`)
    .then(res => {
        dispatch({
            type: GET_SUCCESS_GROUPS,
            payload: res.data
        })
    })
    .catch(error => {
        console.log(error)
        // make some kind of error service ? ex: errorService.log(error) 
    })
}

export const createUserIntoGroupAction = (bodyData, id) => (dispatch, getState) => {
    dispatch({
        type: GET_SUCCESS_FETCHING_GROUPS
    })
    axios({
        method: 'PUT',
        url: `${API}/groups/group/${id}`,
        data: bodyData
    })
    .then(res => {
        dispatch({
            type:GET_SUCCESS_CREATED,
            payload: res.data
        })
        saveDataStorage(res.data)
    })
    .catch(error => {
        console.log(error.response.data.message)
        // make some kind of error service ? ex: errorService.log(error)
    })
}

export const createGroupAction  = (body) => async (dispatch) => {
    dispatch({
        type: GET_SUCCESS_FETCHING_GROUPS
    })
    const totalData = new Promise((dataReturn, errorReturn) => {
        axios({
            method: 'POST',
            url: `${API}/groups/group/`,
            data: body
        })
        .then(res => {
            dataReturn(res.status)
            dispatch({
                type: GET_SUCCESS_CREATED_GROUP,
                payload: res.data
            })
        })
        .catch(error => {
            console.log(error)
            // make some kind of error service ? ex: errorService.log(error) 
            errorReturn(error)
        })
    })

    return totalData
}

