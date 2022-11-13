import React, { useState } from 'react'
import { connect } from 'react-redux'
import { useHistory, Link } from "react-router-dom";
import * as ReactBootStrap from 'react-bootstrap'
import { sendDataRegisterAction } from '../../redux/loginDucks'
import '../../assets/styles/components/Register/register.css'




function Register({ sendDataRegisterAction }) {

    const history = useHistory()
    const [userName, setUserName] = useState(null);
    const [email, setEmail] = useState(null);
    const [password, setPassword] = useState(null);
    const [password2, setPassword2] = useState(null);



    const sendData = async (e) => {
        e.preventDefault();

        const bodyFormData = new FormData()
        bodyFormData.append('username', userName)
        bodyFormData.append('email', email)
        bodyFormData.append('password', password)
        bodyFormData.append('password2', password2)

        const res = await sendDataRegisterAction(bodyFormData)
        if (res.status === 200) {
            history.push('/profile')
        }
    }

    return (
        <div>
        <ReactBootStrap.Form  onSubmit={sendData}  className="total-form">
            <ReactBootStrap.Form.Group className="form-1">
                <ReactBootStrap.Form.Control
                    type="text"
                    placeholder="Enter UserName"
                    onChange={e => setUserName(e.target.value)}
                    value={userName || ''}
                />
            </ReactBootStrap.Form.Group>
            <ReactBootStrap.Form.Group className="form-2">
                <ReactBootStrap.Form.Control
                    type="email"
                    placeholder="Enter email"
                    onChange={e => setEmail(e.target.value)}
                    value={email || ''}
                />
            </ReactBootStrap.Form.Group>
            <ReactBootStrap.Form.Group className="form-3">
                <ReactBootStrap.Form.Control
                    type="password"
                    placeholder="Password"
                    onChange={e => setPassword(e.target.value)}
                    value={password || ''}
                />
            </ReactBootStrap.Form.Group>
            <ReactBootStrap.Form.Group className="form-4">
                <ReactBootStrap.Form.Control
                    type="password"
                    placeholder="Password2"
                    onChange={e => setPassword2(e.target.value)}
                    value={password2 || ''}
                />
            </ReactBootStrap.Form.Group>
            <button  type="submit" className="btn btn-primary" id="btn-login">Create an Account</button>
            <p id="have-account">Already have an account? <Link to="/login" id="log">Login</Link> </p>
        </ReactBootStrap.Form>
        </div>
    )
}

export default connect(null, {sendDataRegisterAction})(Register)
