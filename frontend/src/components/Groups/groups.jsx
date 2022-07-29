import React, { useState } from 'react'
import { connect } from 'react-redux'
import { useHistory } from "react-router-dom"
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, FormGroup, Label, Input } from 'reactstrap'
import { createUserIntoGroupAction, createGroupAction } from '../../redux/groupsDucks'
import Loading from '../LoadingAndError/loading'


const Groups = ({ groups, user, fetching, createUserIntoGroupAction, createGroupAction }) => {
    const history = useHistory()
    const [state, setState] = useState({open: false})
    const [nameGroup, setNameGroup] = useState('')
    const [theme, setTheme] = useState('')
    const [description, setDescription] = useState('')



    const createUserIntoGroup = (id, nameGroup, theme, usersPrev) => {
        const array1 = usersPrev
        const array2 = [user.id]
        const array3 = array1.concat(array2)
        const bodyData = {
            "group_name": nameGroup,
            "theme": theme,
            "users": array3
        }
        createUserIntoGroupAction(bodyData, id)
        try {
            history.push(`/groups/${id}`)
        } catch (error) {
            console.log(error)
            // make some kind of error service ? ex: errorService.log(error) 
        }
    }

    const openModal = () => {
        setState({open: !state.open})
    }

    const returnProfile = (e) => {
        history.push('/profile')
    }

    const createGroup = async () => {
        const body = {
            "user_owner": user.id,
            "group_name": nameGroup,
            "theme": theme,
            "description": description,
            "users": [user.id]
        }
        const newData = await createGroupAction(body)
        if (newData === 200) {
            // window.location.href = window.location.href;
            window.location.href = window.location.href + '';
            openModal()
        }
    }

    if (fetching) return <Loading/>


    return (
        <div>
            <div>
                <h1>Groups</h1>
                {
                    groups.map(item => (
                        <div key={item.id}>
                            <h1>id: {item.id}</h1>
                            <h2>name: {item.group_name} {
                                <Button color="primary" onClick={() => createUserIntoGroup(item.id, item.group_name, item.theme, item.users)}>Join to group</Button>
                            }</h2>
                            <h2>owner: {item.user_owner}</h2>
                            <h2>users in the group: {item.users.length}</h2>
                            <h2>users: [{item.users + ','}]</h2>
                            <br/>
                        </div>
                    ))
                }
                <Button  color="success" onClick={openModal} >create group</Button>
                <Button color="primary" onClick={returnProfile}>Profile</Button>
            </div>
            <Modal isOpen={state.open} >
                <ModalHeader>Create Group</ModalHeader>

                <ModalBody>
                    <FormGroup>
                        <Label>Group Name</Label>
                        <Input
                            type="text"
                            placeholder="name"
                            onChange={(e) => setNameGroup(e.target.value)}
                            value={nameGroup}
                        />
                    </FormGroup>
                    <FormGroup>
                        <Label>Group Theme</Label>
                        <Input
                            type="text"
                            placeholder="theme"
                            onChange={(e) => setTheme(e.target.value)}
                            value={theme}
                        />
                    </FormGroup>
                    <FormGroup>
                        <Label>Group description</Label>
                        <Input
                            type="text"
                            placeholder="description"
                            onChange={(e) => setDescription(e.target.value)}
                            value={description}
                        />
                    </FormGroup>
                </ModalBody>

                <ModalFooter>
                    <Button color="success" onClick={createGroup} >Create Group</Button>
                    <Button color="primary" onClick={openModal}>Close</Button>
                </ModalFooter>
            </Modal>
        </div>
    )
}

const mapStateToProps = (state) => {
    return {
        groups: state.groups.dataGroups,
        user: state.dataLogin.list.user,
        fetching: state.groups.fetching
    }
}

export default connect(mapStateToProps, {createUserIntoGroupAction, createGroupAction})(Groups)