import React, { useState } from 'react'
import { connect } from 'react-redux'
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, FormGroup, Label, Input } from 'reactstrap'
import { sendAnyUserData, getUserDataAction } from "../../redux/loginDucks";
import ModalLanguages from './modalLanguages';



const ModalInformation = ({ token, languages, isOpen, openModal, sendAnyUserData}) => {

    const [name, setName] = useState(null);
    const [lastName, setLastName] = useState(null);
    const [date, setDate] = useState(null);
    const [stateModalLanguages, setStateModalLanguages] = useState({open: false})

    const openModalLanguages = () => {
        setStateModalLanguages({open: !stateModalLanguages.open})
    }


    const sendTotalData = async () => {
        const userFormData = new FormData();
        userFormData.append('name', name)
        userFormData.append('last_name', lastName)
        userFormData.append('birthdate', date)

        if (userFormData != null) {
            const newRes = await sendAnyUserData(userFormData, token)

            console.log(newRes)

            if (newRes.status === 200) {
                openModal()
                getUserDataAction(token)
            }
        }
    }


    return (
        <>
            <Modal isOpen={isOpen}>
                <ModalHeader>Personal Information</ModalHeader>
                <ModalBody>
                    <FormGroup>
                        <Label>What Is Your First Name?</Label>
                        <Input
                            type="text"
                            placeholder="first name"
                            onChange={e => setName(e.target.value)}
                            value={name || ''}
                        />
                    </FormGroup>
                    <FormGroup>
                        <Label>What Is Your Last Name?</Label>
                        <Input
                            type="text"
                            placeholder="last Name"
                            onChange={e => setLastName(e.target.value)}
                            value={lastName || ''}
                        />
                    </FormGroup>
                    <FormGroup>
                        <Label>What Is your birthday?</Label>
                        <Input
                            type="date"
                            id="birthday"
                            name="birthday"
                            onChange={e => setDate(e.target.value)}
                            value={date || ''}
                        />
                    </FormGroup>
                    <FormGroup>
                        <Button color="success" onClick={sendTotalData}>Send</Button>
                    </FormGroup>
                    <FormGroup>
                        <h4>What Is your Languages?</h4>
                        <Button color="primary" onClick={openModalLanguages}>show languages</Button>
                        <ModalLanguages token={token} isOpen={stateModalLanguages.open} openModal={openModalLanguages} languages={languages}/>
                    </FormGroup>
                    <FormGroup>
                        <h4>Goals and Habits</h4>
                        <Button color="primary" onClick={openModalLanguages}>show details</Button>
                        <ModalLanguages token={token} isOpen={stateModalLanguages.open} openModal={openModalLanguages} languages={languages}/>
                    </FormGroup>
                </ModalBody>
                <ModalFooter>
                    <Button color="primary" onClick={openModal}>Close</Button>
                </ModalFooter>
            </Modal>
        </>
    )
}

const mapStateToProps = (state) => {
    return {
      languages: state.dataLogin.languageList
    }
  }

export default connect(mapStateToProps, { sendAnyUserData, getUserDataAction })(ModalInformation)
