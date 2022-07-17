import React, { useState } from "react";
import { useHistory, Link } from "react-router-dom";
import { connect } from 'react-redux'


import { getDataLanguages, sendDataLoginAction } from '../../redux/loginDucks'
import * as ReactBootStrap from 'react-bootstrap'
import Loading from "../LoadingAndError/loading";

import '../../assets/styles/components/Login/login.css'



const Login = ({ fetching, sendDataLoginAction, getDataLanguages }) => {
    // console.log(totalData)
    let history = useHistory();
    const [userName, setUsername] = useState(null)
    const [password, setPassword] = useState(null)


    const handleSubmit = async (e) => {
        e.preventDefault()
        const bodyFormData = new FormData()
        bodyFormData.append('username', userName)
        bodyFormData.append('password', password)
        const res = await sendDataLoginAction(bodyFormData)

        console.log(res)

        if (res.status === 200) {
            getDataLanguages(res.data.authentication.token)
            history.push('/profile')
        }
    }

    if (fetching) return <Loading/>

    return (
        <>
            <ReactBootStrap.Form onSubmit={handleSubmit} className="total-form">
                <ReactBootStrap.Form.Group className='form-1'>
                    <ReactBootStrap.Form.Control
                        type="text"
                        placeholder="Enter userName..."
                        onChange={e => setUsername(e.target.value)}
                        value={userName || ''}
                    />
                </ReactBootStrap.Form.Group>
                <ReactBootStrap.Form.Group className='form-2'>
                    <ReactBootStrap.Form.Control
                        type="password"
                        placeholder="Enter Password..."
                        onChange={e => setPassword(e.target.value)}
                        value={password || ''}
                    />
                </ReactBootStrap.Form.Group>
                <button type='submit' className="btn btn-primary" id="btn-login">Log-In</button>
                <p id="Forgot-password">Forgot your password? <Link to="#" id="reset-it">Reset it</Link> </p>
                <p id="Forgot-password">You want an account? <Link to="/register" id="reset-it">Going to register</Link> </p>
            </ReactBootStrap.Form>
        </>
    )
}

function mapStateToProps(state) {
    return {
        fetching: state.dataLogin.fetching
    }
}

export default connect(mapStateToProps, { sendDataLoginAction, getDataLanguages })(Login)
