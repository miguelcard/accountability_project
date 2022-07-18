import React, {useState} from 'react'
import {Link} from 'react-router-dom'
import {
    Collapse,
    Navbar,
    NavbarToggler,
    NavbarBrand,
    Nav,
    NavItem,
    NavLink
} from 'reactstrap';
import logotype from '../../assets/statics/images/logotype.png'
import '../../assets/styles/components/Header/headerStyle.css'





const Header = (props) => {
    const [isOpen, setIsOpen] = useState(false);

    const toggle = () => setIsOpen(!isOpen);

    return (
        <>
            <Navbar  light expand="lg" className="nav-content">
                {
                    isOpen?
                        <NavbarBrand href="/" className="nav-logotype"><img src={logotype} alt="logo"/></NavbarBrand>
                    :
                    <div></div>
                }
                <NavbarToggler onClick={toggle} />
                <Collapse isOpen={isOpen} navbar className="total-nav">
                        <Nav className="nav-items" navbar>
                            <NavItem className="row-1">
                                <NavLink href="#" id="item">About</NavLink>
                            </NavItem>
                            <NavItem className="row-2">
                                <NavLink href="#" id="item">Pricing</NavLink>
                            </NavItem>
                            <NavItem className="row-3">
                                <NavLink href="#" id="item">Blog</NavLink>
                            </NavItem>
                        </Nav>
                        {
                            !isOpen?
                                <>
                                    <div className="logo-nav-item">
                                        <Link to="/">
                                            <img src={logotype} alt="logo"/>
                                        </Link>
                                    </div>
                                    <div className="nav-left-items">
                                        <Link to="/login" id="login">Sign-In</Link>
                                    </div>
                                </>
                            :
                            <>
                                <div className="nav-left-items">
                                    <Link to="/login" id="login">Sign-In</Link>
                                </div>
                            </>
                        }
                </Collapse>
            </Navbar>
        </>
    );
}

export default Header
