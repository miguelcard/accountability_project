import axios from "axios"

//consts

const initialState = {
    list: [],
    fetching: false
}

const API = process.env.REACT_APP_API_REST


//types
const GET_SUCCESS_REGISTER = 'GET_SUCCESS_REGISTER'
const RUNNING = 'RUNNING'



//reducer
const reducer = (state = initialState, action) => {
    switch (action.type) {
        case RUNNING:
            return {
                ...state,
                fetching: true
            }
        case GET_SUCCESS_REGISTER:
            return {
                ...state,
                list: action.payload,
                fetching: false
            }
        default:
            return state
    }
}

export default reducer


//actions

export const sendDataRegisterAction = (bodyData) => async (dispatch) => {

    dispatch({
        type: RUNNING
    })

    const totalData = await new Promise((DataReturn, errorReturn) => {
        axios({
            method: 'POST',
            url: `${API}/users/user/`,
            headers: { "Content-Type": "application/json" },
            data: bodyData
        })
        .then(res => {
            console.log(res.data)
            DataReturn(res.status)
            dispatch({
                type: GET_SUCCESS_REGISTER,
                payload: res.data
            })
        })
        .catch(error => {
            console.log(error.response.data.message)
            errorReturn(error.response.data.message)
        })
    })
    console.log(totalData)
    return totalData
}