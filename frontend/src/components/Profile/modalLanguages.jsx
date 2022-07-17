import React, { useState } from 'react'
import {Button, Modal, ModalHeader, ModalBody, ModalFooter, FormGroup} from 'reactstrap'
import Chip from '@material-ui/core/Chip';
import { Avatar } from '@material-ui/core';
import DoneIcon from '@material-ui/icons/Done';
import Paper from '@material-ui/core/Paper';
import { connect } from 'react-redux';
import { sendUpdatedLanguages } from '../../redux/loginDucks';


const ModalLanguages = ({ token, isOpen, openModal, languages, sendUpdatedLanguages}) => {

    const [chipData, setChipData] = useState(languages)

    const handleDelete = (chipToDelete) => () => {
        setChipData((chips) => chips.filter((chip) => chip.id !== chipToDelete.id));
        sendUpdatedLanguages(token, chipToDelete.id)
        openModal()
    };

    return (
      <>
        <Modal isOpen={isOpen}>
          <ModalHeader>Personal Information</ModalHeader>
          <ModalBody>
            <FormGroup>
              <div>
                <Paper component="ul">
                  {chipData.map((data) => {
                    return (
                      <li key={data.id}>
                        <Chip
                          key={data.id}
                          avatar={<Avatar>L</Avatar>}
                          label={data.name}
                          onDelete={handleDelete(data)}
                          deleteIcon={<DoneIcon />}
                          color="primary"
                        />
                      </li>
                    );
                  })}
                </Paper>
              </div>
            </FormGroup>
          </ModalBody>
          <ModalFooter>
            <Button color="primary" onClick={openModal}>
              Previous
            </Button>
          </ModalFooter>
        </Modal>
      </>
    );
}

const mapStateToProps = (state) => {
    return {
        id: state.dataLogin.list.user.id,
        user: state.dataLogin.list.user
    }
}

export default connect(mapStateToProps, { sendUpdatedLanguages })(ModalLanguages)
