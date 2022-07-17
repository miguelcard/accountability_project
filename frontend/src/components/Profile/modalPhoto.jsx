import React, { useState } from 'react'
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, FormGroup, Label, Input } from 'reactstrap'
import { connect } from 'react-redux'
import { sendProfilePhotoAction, getUserDataAction } from '../../redux/loginDucks'




const ModalPhoto = ({ openModal, isOpen, sendProfilePhotoAction, getUserDataAction, token }) => {

    // console.log(props)

    const [profilePhoto, setProfilePhoto] = useState(null)

    const sendFiles = (e) => {
        console.log(e)
        setProfilePhoto(e)
    }

    const sendTotalData = async () => {
        const bodyData = new FormData()

        if (profilePhoto != null) {
            for (let i = 0; i < profilePhoto.length; i++) {
                bodyData.append('profile_photo', profilePhoto[i])
            }
            const res = await sendProfilePhotoAction(bodyData, token)
            console.log(res)
            if (res.status === 200) {
                openModal()
                // window.location.href = window.location.href + '';
                getUserDataAction(token)
            }
        }
    }



    return (
        <>
            <Modal isOpen={isOpen}>
                <ModalHeader>add photo</ModalHeader>
                <ModalBody>
                    <FormGroup>
                        <Label>add your profile photo</Label>
                        <Input
                            type="file"
                            name="file"
                            multiple
                            onChange={e => sendFiles(e.target.files)}
                        />
                    </FormGroup>
                </ModalBody>
                <ModalFooter>
                    <Button color="success" onClick={sendTotalData}>send</Button>
                    <Button color="primary" onClick={openModal} >Close</Button>
                </ModalFooter>
            </Modal>
        </>
    )
}

export default connect(null, { sendProfilePhotoAction, getUserDataAction })(ModalPhoto)
