import React, { useState } from 'react'
import { connect } from 'react-redux'
import { sendProfilePhotoAction, getUserDataAction } from '../../redux/loginDucks'




const ModalPhoto = ({ sendProfilePhotoAction, getUserDataAction, token }) => {

    const [profilePhoto, setProfilePhoto] = useState(null)

    const sendFiles = (e) => {
        setProfilePhoto(e)
    }

    const sendTotalData = async () => {
        const bodyData = new FormData()

        if (profilePhoto != null) {
            for (let i = 0; i < profilePhoto.length; i++) {
                bodyData.append('profile_photo', profilePhoto[i])
            }
            const res = await sendProfilePhotoAction(bodyData, token)
            if (res.status === 200) {
                // window.location.href = window.location.href + '';
                getUserDataAction(token)
            }
        }
    }



    return (
        <>
            <div>
                <h2>add photo</h2>
                <div>
                    <div>
                        <span>add your profile photo</span>
                        <input
                            type="file"
                            name="file"
                            multiple
                            onChange={e => sendFiles(e.target.files)}
                        />
                    </div>
                </div>
                <div>
                    <button color="success" onClick={sendTotalData}>send</button>
                    <button color="primary" >Close</button>
                </div>
            </div>
        </>
    )
}

export default connect(null, { sendProfilePhotoAction, getUserDataAction })(ModalPhoto)
