import * as Yup from 'yup';

const validationSchemas = [
    Yup.object().shape({
        name: Yup
            .string()
            .required('Name is required'),
        email: Yup
            .string()
            .email('Enter a valid email')
            .required('Email is required'),
        password: Yup
            .string()
            .min(8, 'Password should be of minimum 8 characters length')
            .required('Password is required'),
    }),
    Yup.object().shape({
        username: Yup
            .string()
            .required('username is required')
            .min(3, 'Username must be at least 3 characters')
            .max(20, 'Username must be at most 20 characters')
            .matches(/^[a-zA-Z0-9_-]+$/, 'Username can only contain letters, numbers, dashes, and underscores')
            .test('unique', 'Username is already taken', async function (value) {
                const isUsernameTaken: boolean = await checkIfUsernameIsTaken(value);
                return !isUsernameTaken;
            })
    })
];


// TODO
const checkIfUsernameIsTaken = async (value: string): Promise<boolean> => {
    // Your implementation to check if the username is already taken goes here
    return value === 'migueluy';
};


export default validationSchemas;