import { FC, useState } from 'react';

interface GenericIconProps {
    icon: string;
    onClick?: () => void;
    onHoverStyle?: React.CSSProperties;
    className?: string;
    width?: number | string;
    height?: number | string;
    fill?: string;
}

const GenericIcon: FC<GenericIconProps> = ({
    icon,
    onClick,
    onHoverStyle,
    className = '',
    width = 24,
    height = 24,
    fill = 'none'
}) => {
    const [isHovered, setIsHovered] = useState(false);


    if (icon === 'github') {
        return (
            <svg
                width={width}
                height={height}
                fill={fill}
                stroke="currentColor"
                strokeWidth="1.5"
                viewBox="0 0 24 24"
                strokeLinecap="round"
                strokeLinejoin="round"
                xmlns="http://www.w3.org/2000/svg"
                className={className}
                style={{
                    cursor: onClick ? 'pointer' : 'default',
                    ...(isHovered && onHoverStyle)
                }}
                onClick={onClick}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                <path d='M3.5 15.668q.675.081 1 .618c.326.537 1.537 2.526 2.913 2.526H9.5m5.672-3.513q.823 1.078.823 1.936V21m-5.625-5.609q-.87.954-.869 1.813V21' />
                <path d='M15.172 15.299c1.202-.25 2.293-.682 3.14-1.316 1.448-1.084 2.188-2.758 2.188-4.411 0-1.16-.44-2.243-1.204-3.16-.425-.511.819-3.872-.286-3.359-1.105.514-2.725 1.198-3.574.947-.909-.268-1.9-.416-2.936-.416-.9 0-1.766.111-2.574.317-1.174.298-2.296-.363-3.426-.848-1.13-.484-.513 3.008-.849 3.422C4.921 7.38 4.5 8.44 4.5 9.572c0 1.653.895 3.327 2.343 4.41.965.722 2.174 1.183 3.527 1.41' />
            </svg>
        );
    }

    if (icon === 'flag') {
        return (
            <svg
                width={width}
                height={height}
                fill={fill}
                stroke="currentColor"
                strokeWidth="1.5"
                viewBox="0 0 24 24"
                strokeLinecap="round"
                strokeLinejoin="round"
                xmlns="http://www.w3.org/2000/svg"
                className={className}
                style={{
                    cursor: onClick ? 'pointer' : 'default',
                    ...(isHovered && onHoverStyle)
                }}
                onClick={onClick}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                <path d='m4.75 14 13.78-4.04c.96-.282.96-1.638 0-1.92L4.75 4m0 10V4m0 10v7m0-17V3' />
            </svg>
        );
    }

    return null;
};

export default GenericIcon;
