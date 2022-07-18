import axios from 'axios'


//constants

const dataInitial = {
    usersList: []
}

//types
const GET_USERS_OK = 'GET_USERS_OK'

//reducer

export default function reducer(state = dataInitial, action) {
    switch (action.type) {
        case GET_USERS_OK:
            return {
                ...state,
                usersList: action.payload,
            }
        default:
            return state;
    }
}


//actions
const API = process.env.REACT_APP_API_REST

export const getUsersAction = () => async (dispatch, getState) => {
    try {
        const res = await axios.get(`${API}/users/user/`)
        dispatch({
            type: GET_USERS_OK,
            payload: res.data
        })
    } catch (error) {
        console.log(error)
    }
}