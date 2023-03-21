export interface FormValues {
    name: string;
    email: string;
    password: string;
    username: string;
}

export const initialValues: FormValues = {
    name: '',
    email: '',
    password: '',
    username: ''
};