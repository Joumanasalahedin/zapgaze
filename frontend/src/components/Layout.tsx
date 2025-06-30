import { FC } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import styles from './Layout.module.css';
import { useLayoutFlags } from '../App';

const Layout: FC = () => {
    const { flags } = useLayoutFlags();

    return (
        <div>
            {flags.showHeader && <Header />}
            <main className={styles.main}>
                <Outlet />
            </main>
            {flags.showFooter && <Footer />}
        </div>
    );
};

export default Layout;