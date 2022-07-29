import axios from 'axios'
import React, {useState} from 'react'
import { connect } from 'react-redux'
import { useHistory } from 'react-router'
import { Button, Form, FormText,FormGroup, Label, Input } from 'reactstrap'
import Loading from '../LoadingAndError/loading'

const API = process.env.REACT_APP_API_REST



const Group = ({ group, fetching, user }) => {
    const [contentFiles, setContentFiles] = useState(null)
    const [content, setContent] = useState(null)
    const history = useHistory()


    const sendFiles = (e) => {
        setContentFiles(e)
    }


    const sendTotalData = async () => {
        const bodyData = new FormData()
        bodyData.append('user_owner', user.id)
        bodyData.append('contents', content)

            if (contentFiles != null) {
                for (let i = 0; i < contentFiles.length; i++) {
                    bodyData.append('images', contentFiles[i])
                }
            }
        await axios({
            method: 'POST',
            url: `${API}/posts/post/`,
            data: bodyData
        })
        .then(res => {
            // console.log(res.data)
        })
        .catch(error => {
            console.log(error)
        })
    }

    const redirectToPreview = () => {
        history.push('/groups')
    }



    if (fetching) return <Loading/>

    return (
        <div>
            <h1>welcome to {group.group_name}</h1>
            <h2>theme: {group.theme}</h2>
            <h2>description: {group.description}</h2>
            <br/> <br/>
            <div>
                <Form >
                    <FormGroup>
                        <Label for="exampleFile">Post</Label>
                        <FormText color="muted">
                            <Input
                                type="textarea"
                                placeholder="Whats UP!!"
                                className="w-50"
                                onChange={(e) => setContent(e.target.value)}
                                value={content || ''}
                            />
                            <Input
                                type="file"
                                name="file"
                                multiple
                                onChange={e => sendFiles(e.target.files)}
                            />
                        </FormText>
                    </FormGroup>
                    <Button color="success" onClick={() => sendTotalData()}>Send</Button>
                    <Button color="primary" onClick={() => redirectToPreview()}>go to previous</Button>
                </Form>

                {/* <div>
                    <img
                        src={"http://127.0.0.1:8000/media/assets/images/groups/pic-person-01.jpg"}
                        width="100"
                        height="100"
                    />
                </div> */}

            </div>
        </div>
    )
}

const mapStateToProps = (state) => {
    return {
        group: state.groups.addUserIntoGroup,
        fetching: state.groups.fetching,
        user: state.dataLogin.list.user
    }
}

export default connect(mapStateToProps)(Group)
