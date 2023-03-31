import React, { useState } from 'react'
import { connect } from 'react-redux'
import { getUserDataAction, sendAnyUserData } from '../../redux/loginDucks';

// define an interface for the props comming in, and relplace the "any" below for TS

// const ModalAboutMe: React.FC<any> = ({ token, openModal, isOpen, getUserDataAction, sendAnyUserData }) => {
    const ModalAboutMe = ({ token, getUserDataAction, sendAnyUserData }) => {

    const [stateText, setStateText] = useState(null);

    const sendTotalText = async () => {
        const bodyFormData = new FormData()
        bodyFormData.append('about', stateText)

        if (stateText != null) {
            const res = await sendAnyUserData(bodyFormData, token)
            if (res.status === 200) {
                getUserDataAction(token)
            }
        }

    }


    return (
        <>
            <div>
                <span>About me motherfuckers</span>
                <div>
                        <span>Tell us about you</span>
                        <input
                            type="textarea"
                            placeholder="About you"
                            onChange={e => setStateText(e.target.value)}
                            value={stateText || ''}
                        />
                </div>
                <div>
                    <button color="success" onClick={sendTotalText}>Send</button>
                    <button color="primary" >Close</button>
                </div>
            </div>
        </>
    )
}

export default connect(null, { getUserDataAction, sendAnyUserData })(ModalAboutMe)
