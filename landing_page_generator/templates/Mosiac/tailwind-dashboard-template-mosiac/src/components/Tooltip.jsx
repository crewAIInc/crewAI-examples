import React, { useState } from 'react';
import Transition from '../utils/Transition';

function Tooltip({
  children,
  className,
  bg,
  size,
  position,
}) {

  const [tooltipOpen, setTooltipOpen] = useState(false);

  const positionOuterClasses = (position) => {
    switch (position) {
      case 'right':
        return 'left-full top-1/2 -translate-y-1/2';
      case 'left':
        return 'right-full top-1/2 -translate-y-1/2';
      case 'bottom':
        return 'top-full left-1/2 -translate-x-1/2';
      default:
        return 'bottom-full left-1/2 -translate-x-1/2';
    }
  }

  const sizeClasses = (size) => {
    switch (size) {
      case 'lg':
        return 'min-w-72 px-3 py-2';
      case 'md':
        return 'min-w-56 px-3 py-2';
      case 'sm':
        return 'min-w-44 px-3 py-2';
      default:
        return 'px-3 py-2';
    }
  };

  const colorClasses = (bg) => {
    switch (bg) {
      case 'light':
        return 'bg-white text-gray-600 border-gray-200';
      case 'dark':
        return 'bg-gray-800 text-gray-100 border-gray-700/60';
      default:
        return 'text-gray-600 bg-white dark:bg-gray-800 dark:text-gray-100 border-gray-200 dark:border-gray-700/60';
    }
  };    

  const positionInnerClasses = (position) => {
    switch (position) {
      case 'right':
        return 'ml-2';
      case 'left':
        return 'mr-2';
      case 'bottom':
        return 'mt-2';
      default:
        return 'mb-2';
    }
  };

  return (
    <div
      className={`relative ${className}`}
      onMouseEnter={() => setTooltipOpen(true)}
      onMouseLeave={() => setTooltipOpen(false)}
      onFocus={() => setTooltipOpen(true)}
      onBlur={() => setTooltipOpen(false)}
    >
      <button className="block" aria-haspopup="true" aria-expanded={tooltipOpen} onClick={(e) => e.preventDefault()}>
        <svg className="fill-current text-gray-400 dark:text-gray-500" width="16" height="16" viewBox="0 0 16 16">
          <path d="M8 0C3.6 0 0 3.6 0 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 12c-.6 0-1-.4-1-1s.4-1 1-1 1 .4 1 1-.4 1-1 1zm1-3H7V4h2v5z" />
        </svg>
      </button>
      <div className={`z-10 absolute ${positionOuterClasses(position)}`}>
        <Transition
          show={tooltipOpen}
          tag="div"
          className={`rounded-lg border overflow-hidden shadow-lg ${sizeClasses(size)} ${colorClasses(bg)} ${positionInnerClasses(position)}`}
          enter="transition ease-out duration-200 transform"
          enterStart="opacity-0 -translate-y-2"
          enterEnd="opacity-100 translate-y-0"
          leave="transition ease-out duration-200"
          leaveStart="opacity-100"
          leaveEnd="opacity-0"
        >
          {children}
        </Transition>
      </div>
    </div>
  );
}

export default Tooltip;