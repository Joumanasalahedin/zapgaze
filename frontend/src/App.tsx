import {
    FC,
    useEffect,
    Suspense,
    lazy,
    createContext,
    useContext,
    useState,
    useCallback
} from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LoadingSpinner from './components/LoadingSpinner';

interface LayoutFlags {
    showHeader: boolean;
    showFooter: boolean;
}

const LayoutContext = createContext<{
    flags: LayoutFlags;
    setFlags: (flags: LayoutFlags) => void;
}>({
    flags: { showHeader: true, showFooter: true },
    setFlags: () => { }
});

export const useLayoutFlags = () => useContext(LayoutContext);

const HomePage = lazy(() => import('./pages/HomePage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const TestPage = lazy(() => import('./pages/TestPage'));
const ResultsPage = lazy(() => import('./pages/ResultsPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));
const IntakeQuestionnairePage = lazy(() => import('./pages/IntakeQuestionnairePage'));

const RouteWrapper: FC<{
    component: React.ComponentType;
    layoutFlags: LayoutFlags;
}> = ({ component: Component, layoutFlags }) => {
    const { setFlags } = useLayoutFlags();

    useEffect(() => {
        setFlags(layoutFlags);
    }, [setFlags, layoutFlags.showHeader, layoutFlags.showFooter]);

    return <Component />;
};

const App: FC = () => {
    const [layoutFlags, setLayoutFlags] = useState<LayoutFlags>({
        showHeader: true,
        showFooter: true
    });

    const memoizedSetFlags = useCallback((flags: LayoutFlags) => {
        setLayoutFlags(flags);
    }, []);

    return (
        <LayoutContext.Provider value={{ flags: layoutFlags, setFlags: memoizedSetFlags }}>
            <Suspense fallback={<LoadingSpinner />}>
                <Routes>
                    <Route path="/" element={<Layout />}>
                        <Route
                            index
                            element={
                                <RouteWrapper
                                    component={HomePage}
                                    layoutFlags={{ showHeader: true, showFooter: true }}
                                />
                            }
                        />
                        <Route
                            path="about"
                            element={
                                <RouteWrapper
                                    component={AboutPage}
                                    layoutFlags={{ showHeader: true, showFooter: true }}
                                />
                            }
                        />
                        <Route
                            path="intake"
                            element={
                                <RouteWrapper
                                    component={IntakeQuestionnairePage}
                                    layoutFlags={{ showHeader: true, showFooter: true }}
                                />
                            }
                        />
                        <Route
                            path="test"
                            element={
                                <RouteWrapper
                                    component={TestPage}
                                    layoutFlags={{ showHeader: false, showFooter: false }}
                                />
                            }
                        />
                        <Route
                            path="results"
                            element={
                                <RouteWrapper
                                    component={ResultsPage}
                                    layoutFlags={{ showHeader: true, showFooter: true }}
                                />
                            }
                        />
                        <Route
                            path="*"
                            element={
                                <RouteWrapper
                                    component={NotFoundPage}
                                    layoutFlags={{ showHeader: false, showFooter: false }}
                                />
                            }
                        />
                    </Route>
                </Routes>
            </Suspense>
        </LayoutContext.Provider>
    );
};

export default App;
