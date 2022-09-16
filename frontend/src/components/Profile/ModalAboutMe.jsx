import React, { useState } from 'react'
import { connect } from 'react-redux'
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, FormGroup, Label, Input } from 'reactstrap'
import { getUserDataAction, sendAnyUserData } from '../../redux/loginDucks';


const ModalAboutMe = ({ token, openModal, isOpen, getUserDataAction, sendAnyUserData }) => {

    const [stateText, setStateText] = useState(null);

    const sendTotalText = async () => {
        const bodyFormData = new FormData()
        bodyFormData.append('about', stateText)

        if (stateText != null) {
            const res = await sendAnyUserData(bodyFormData, token)
            if (res.status === 200) {
                openModal()
                getUserDataAction(token)
            }
        }

    }


    return (
        <>
            <Modal isOpen={isOpen}>
                <ModalHeader>About me motherfuckers</ModalHeader>
                <ModalBody>
                    <FormGroup>
                        <Label>Tell us about you</Label>
                        <Input
                            type="textarea"
                            placeholder="About you"
                            onChange={e => setStateText(e.target.value)}
                            value={stateText || ''}
                        />
                    </FormGroup>
                </ModalBody>
                <ModalFooter>
                    <Button color="success" onClick={sendTotalText}>Send</Button>
                    <Button color="primary" onClick={openModal}>Close</Button>
                </ModalFooter>
            </Modal>
        </>
    )
}

export default connect(null, { getUserDataAction, sendAnyUserData })(ModalAboutMe)
